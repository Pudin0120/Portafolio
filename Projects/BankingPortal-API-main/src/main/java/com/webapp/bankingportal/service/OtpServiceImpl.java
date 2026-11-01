package com.webapp.bankingportal.service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.security.SecureRandom;
import java.util.concurrent.CompletableFuture;

import org.springframework.cache.CacheManager;
import org.springframework.stereotype.Service;

import com.webapp.bankingportal.entity.OtpInfo;
import com.webapp.bankingportal.exception.AccountDoesNotExistException;
import com.webapp.bankingportal.exception.InvalidOtpException;
import com.webapp.bankingportal.exception.OtpRetryLimitExceededException;
import com.webapp.bankingportal.repository.OtpInfoRepository;
import com.webapp.bankingportal.util.ValidationUtil;
import com.webapp.bankingportal.util.ApiMessages;

import lombok.RequiredArgsConstructor;
import lombok.val;

@Service
@RequiredArgsConstructor
public class OtpServiceImpl implements OtpService {

    public static final int OTP_ATTEMPTS_LIMIT = 3;
    public static final int OTP_EXPIRY_MINUTES = 5;
    public static final int OTP_RESET_WAITING_TIME_MINUTES = 10;
    public static final int OTP_RETRY_LIMIT_WINDOW_MINUTES = 15;

    private static final String OTP_ATTEMPTS_CACHE = "otpAttempts";
    private static final String OTP_LIMIT_REACHED_CACHE = "otpLimitReachedAt";
    private static final SecureRandom SECURE_RANDOM = new SecureRandom();

    private final CacheManager cacheManager;
    private final EmailService emailService;
    private final OtpInfoRepository otpInfoRepository;
    private final ValidationUtil validationUtil;

    @Override
    public String generateOTP(String accountNumber) {
        if (!validationUtil.doesAccountExist(accountNumber)) {
            throw new AccountDoesNotExistException(ApiMessages.ACCOUNT_NOT_FOUND.getMessage());
        }

        validateOtpWithinRetryLimit(accountNumber);
        val existingOtpInfo = otpInfoRepository.findByAccountNumber(accountNumber);
        incrementOtpAttempts(accountNumber);

        if (existingOtpInfo == null || isOtpExpired(existingOtpInfo)) {
            return generateNewOTP(accountNumber);
        }

        return existingOtpInfo.getOtp();
    }

    private void validateOtpWithinRetryLimit(String accountNumber) {
        if (!isOtpRetryLimitExceeded(accountNumber)) {
            return;
        }

        val now = LocalDateTime.now();
        val limitReachedAt = getOtpLimitReachedAt(accountNumber);
        val elapsedMinutes = limitReachedAt == null
                ? 0
                : limitReachedAt.until(now, ChronoUnit.MINUTES);
        val waitingMinutes = Math.max(0, OTP_RESET_WAITING_TIME_MINUTES - elapsedMinutes);

        throw new OtpRetryLimitExceededException(
                String.format(ApiMessages.OTP_GENERATION_LIMIT_EXCEEDED.getMessage(), waitingMinutes));
    }

    private boolean isOtpRetryLimitExceeded(String accountNumber) {
        if (getOtpAttempts(accountNumber) < OTP_ATTEMPTS_LIMIT) {
            return false;
        }

        val now = LocalDateTime.now();
        val limitReachedAt = getOtpLimitReachedAt(accountNumber);
        if (limitReachedAt == null) {
            cacheOtpLimitReachedAt(accountNumber, now);
            return true;
        }

        if (!limitReachedAt.plusMinutes(OTP_RESET_WAITING_TIME_MINUTES).isAfter(now)) {
            resetOtpAttempts(accountNumber);
            return false;
        }

        return true;
    }

    private LocalDateTime getOtpLimitReachedAt(String accountNumber) {
        val cache = cacheManager.getCache(OTP_LIMIT_REACHED_CACHE);
        return cache == null ? null : cache.get(accountNumber, LocalDateTime.class);
    }

    private void cacheOtpLimitReachedAt(String accountNumber, LocalDateTime time) {
        val cache = cacheManager.getCache(OTP_LIMIT_REACHED_CACHE);
        if (cache != null) {
            cache.put(accountNumber, time);
        }
    }

    private void incrementOtpAttempts(String accountNumber) {
        if (!validationUtil.doesAccountExist(accountNumber)) {
            throw new AccountDoesNotExistException(ApiMessages.ACCOUNT_NOT_FOUND.getMessage());
        }

        val cache = cacheManager.getCache(OTP_ATTEMPTS_CACHE);
        if (cache != null) {
            int attempts = getOtpAttempts(accountNumber) + 1;
            cache.put(accountNumber, attempts);
            if (attempts >= OTP_ATTEMPTS_LIMIT && getOtpLimitReachedAt(accountNumber) == null) {
                cacheOtpLimitReachedAt(accountNumber, LocalDateTime.now());
            }
        }
    }

    private void resetOtpAttempts(String accountNumber) {
        val attemptsCache = cacheManager.getCache(OTP_ATTEMPTS_CACHE);
        if (attemptsCache != null) {
            attemptsCache.put(accountNumber, 0);
        }

        val limitCache = cacheManager.getCache(OTP_LIMIT_REACHED_CACHE);
        if (limitCache != null) {
            limitCache.evict(accountNumber);
        }
    }

    private int getOtpAttempts(String accountNumber) {
        var otpAttempts = 0;
        val cache = cacheManager.getCache(OTP_ATTEMPTS_CACHE);
        if (cache == null) {
            return otpAttempts;
        }

        val value = cache.get(accountNumber, Integer.class);
        if (value != null) {
            otpAttempts = value;
        }

        return otpAttempts;
    }

    private String generateNewOTP(String accountNumber) {
        val otpValue = 100_000 + SECURE_RANDOM.nextInt(900_000);
        val otp = String.valueOf(otpValue);

        otpInfoRepository.save(new OtpInfo(accountNumber, otp, LocalDateTime.now()));

        return otp;
    }

    @Override
    public CompletableFuture<Void> sendOTPByEmail(String email, String name, String accountNumber, String otp) {
        val emailText = emailService.getOtpLoginEmailTemplate(name, "xxx" + accountNumber.substring(3), otp);
        return emailService.sendEmail(email, ApiMessages.EMAIL_SUBJECT_OTP.getMessage(), emailText);
    }

    @Override
    public boolean validateOTP(String accountNumber, String otp) {
        val otpInfo = otpInfoRepository.findByAccountNumberAndOtp(accountNumber, otp);
        if (otpInfo == null) {
            throw new InvalidOtpException(ApiMessages.OTP_INVALID_ERROR.getMessage());
        }

        if (isOtpExpired(otpInfo)) {
            return false;
        }

        // A valid OTP is single-use: consume it immediately after successful verification.
        otpInfoRepository.delete(otpInfo);
        return true;
    }

    private boolean isOtpExpired(OtpInfo otpInfo) {
        val now = LocalDateTime.now();
        val generatedAt = otpInfo.getGeneratedAt();
        val expired = generatedAt.isBefore(now.minusMinutes(OTP_EXPIRY_MINUTES));
        if (expired) {
            otpInfoRepository.delete(otpInfo);
        }

        return expired;
    }

}
