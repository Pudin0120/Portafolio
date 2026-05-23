package pers.hdh.utils;

import com.sun.mail.util.MailSSLSocketFactory;

import javax.mail.*;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeMessage;
import java.util.Properties;

public class MailUtils {

    // /
    private static String[] from={ "", ""};

    /**
     * 
     * @param to 
     * @param msg 
     */
    public static void sendMail(String to, String msg) throws Exception {

        // 1.
        Properties prop = new Properties();
        // 
        prop.setProperty("mail.host", "smtp.qq.com");
        // 
        prop.setProperty("mail.transport.protocol", "smtp");
        // 
        prop.setProperty("mail.smtp.auth", "true");

        /*
            qqssl
        */
        MailSSLSocketFactory sf = new MailSSLSocketFactory();
        sf.setTrustAllHosts(true);
        prop.setProperty("mail.smtp.ssl.enable", "true");
        prop.put("mail.smtp.ssl.socketFactory", sf);

        Session session = Session.getInstance(prop,  new Authenticator() {
            public PasswordAuthentication getPasswordAuthentication() {
                //
                return new PasswordAuthentication(from[0], from[1]);
            }
        });

        // 2.
        Message message = new MimeMessage(session);
        // 2.1 
        message.setFrom(new InternetAddress(from[0]));
        // 2.2 
        message.setRecipient(Message.RecipientType.TO, new InternetAddress(to));
        // 2.3 
        message.setSubject("");
        // 2.4 
        message.setContent("<h1><a href='http://localhost:8080/maildemo/ActiveServlet?uid="+msg+"'></a></h1>", "text/html;charset=utf-8");

        // 3.
        Transport.send(message);
    }
}
