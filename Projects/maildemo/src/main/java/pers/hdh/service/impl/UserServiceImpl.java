package pers.hdh.service.impl;

import pers.hdh.dao.UserDao;
import pers.hdh.dao.impl.UserDaoImpl;
import pers.hdh.domain.User;
import pers.hdh.service.UserService;
import pers.hdh.utils.MailUtils;

import java.sql.SQLException;

public class UserServiceImpl implements UserService {

    /**
     * 
     * @param user
     */
    @Override
    public void add(User user) throws Exception {
        // 
        UserDao dao = new UserDaoImpl();
        dao.add(user);

        // 
        MailUtils.sendMail(user.getEmail(), user.getUid());
    }

    /**
     * id
     * @param uid
     * @return
     */
    @Override
    public User getUser(String uid) throws SQLException {
        UserDao dao = new UserDaoImpl();
        return dao.getUser(uid);
    }

    /**
     * 
     * @param user
     */
    @Override
    public void update(User user) throws SQLException {
        UserDao dao = new UserDaoImpl();
        dao.update(user);
    }
}
