package com.webapp.bankingportal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.time.LocalDateTime;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.cache.CacheManager;
import org.springframework.cache.concurrent.ConcurrentMapCacheManager;

import com.webapp.bankingportal.entity.OtpInfo;
import com.webapp.bankingportal.exception.InvalidOtpException;
import com.webapp.bankingportal.exception.OtpRetryLimitExceededException;
import com.webapp.bankingportal.repository.OtpInfoRepository;
import com.webapp.bankingportal.service.EmailService;
import com.webapp.bankingportal.service.OtpServiceImpl;
import com.webapp.bankingportal.util.ValidationUtil;

import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

class OtpServiceTests {

    private static final String ACCOUNT_NUMBER = "123456";

    @Mock
    private EmailService emailService;

    @Mock
    private OtpInfoRepository otpInfoRepository;

    @Mock
    private ValidationUtil validationUtil;

    private CacheManager cacheManager;
    private OtpServiceImpl otpService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        cacheManager = new ConcurrentMapCacheManager("otpAttempts", "otpLimitReachedAt");
        otpService = new OtpServiceImpl(cacheManager, emailService, otpInfoRepository, validationUtil);
        when(validationUtil.doesAccountExist(ACCOUNT_NUMBER)).thenReturn(true);
    }

    @Test
    void generatesSixDigitOtpUsingPersistedRecord() {
        when(otpInfoRepository.findByAccountNumber(ACCOUNT_NUMBER)).thenReturn(null);

        String otp = otpService.generateOTP(ACCOUNT_NUMBER);

        assertTrue(otp.matches("[0-9]{6}"));
        verify(otpInfoRepository).save(any(OtpInfo.class));
    }

    @Test
    void consumesOtpAfterSuccessfulVerification() {
        OtpInfo otpInfo = new OtpInfo(ACCOUNT_NUMBER, "123456", LocalDateTime.now());
        when(otpInfoRepository.findByAccountNumberAndOtp(ACCOUNT_NUMBER, "123456"))
                .thenReturn(otpInfo)
                .thenReturn(null);

        assertTrue(otpService.validateOTP(ACCOUNT_NUMBER, "123456"));
        verify(otpInfoRepository).delete(otpInfo);
        assertThrows(InvalidOtpException.class,
                () -> otpService.validateOTP(ACCOUNT_NUMBER, "123456"));
    }

    @Test
    void rejectsExpiredOtp() {
        OtpInfo expiredOtp = new OtpInfo(
                ACCOUNT_NUMBER, "123456", LocalDateTime.now().minusMinutes(6));
        when(otpInfoRepository.findByAccountNumberAndOtp(ACCOUNT_NUMBER, "123456"))
                .thenReturn(expiredOtp);

        assertFalse(otpService.validateOTP(ACCOUNT_NUMBER, "123456"));
        verify(otpInfoRepository).delete(expiredOtp);
    }

    @Test
    void appliesRetryLimitPerAccount() {
        OtpInfo existingOtp = new OtpInfo(ACCOUNT_NUMBER, "123456", LocalDateTime.now());
        when(otpInfoRepository.findByAccountNumber(ACCOUNT_NUMBER)).thenReturn(existingOtp);

        assertEquals("123456", otpService.generateOTP(ACCOUNT_NUMBER));
        assertEquals("123456", otpService.generateOTP(ACCOUNT_NUMBER));
        assertEquals("123456", otpService.generateOTP(ACCOUNT_NUMBER));

        assertThrows(OtpRetryLimitExceededException.class,
                () -> otpService.generateOTP(ACCOUNT_NUMBER));
    }
}
