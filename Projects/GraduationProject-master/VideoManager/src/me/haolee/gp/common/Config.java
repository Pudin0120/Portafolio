package me.haolee.gp.common;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public class Config {
	public static Properties properties = null;
	
	/**
	 * 
	 * @param configFileName 
	 */
	public static void readConfigFile(String configFileName) {
		//
		FileInputStream fileInputStream = null;
		InputStream inputStream = null;
		try {
			fileInputStream = new FileInputStream(configFileName);
			inputStream = new BufferedInputStream(fileInputStream);
			properties = new Properties();
			properties.load(inputStream);
		} catch (Exception e) {
			e.printStackTrace();
		}finally {
			try {
				if(fileInputStream!=null)fileInputStream.close();
				if(inputStream!=null)inputStream.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}
	
	/**
	 * 
	 * @param key 
	 * @param defaultValue value
	 * @return value
	 */
	public static String getValue(String key, String defaultValue) {
		return properties.getProperty(key,defaultValue);
	}
}
