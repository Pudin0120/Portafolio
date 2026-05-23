package me.haolee.gp.clientside;

import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.util.ArrayList;
import java.util.concurrent.Callable;
import javax.swing.DefaultListModel;
import javax.swing.JOptionPane;
import javax.swing.SwingUtilities;
import me.haolee.gp.common.CommandWord;
import me.haolee.gp.common.Config;
import me.haolee.gp.common.Packet;



public class CatagoryListCallable implements Callable<Integer> {
	
	/*
	 * call
	 * 
	 * */
	private String serverIP = null;
	private int serverPort = -1;
	private CommandWord mode = null;
	private DefaultListModel<String> categoryListModel = null;
	/**/
	public CatagoryListCallable(CommandWord mode
			,DefaultListModel<String> categoryListModel) {
		this.serverIP = Config.getValue("serverIP", "127.0.0.1");
		this.serverPort = Integer.valueOf(Config.getValue("serverPort", "10000"));
		this.mode = mode;
		this.categoryListModel = categoryListModel;
	}

	@Override
	public Integer call() throws Exception {
		/**/
		Socket socketToServer = null;
		InputStream inputStream = null;
		OutputStream outputStream =null;
		/**/
		ObjectOutputStream objectOutputStream = null;
		ObjectInputStream objectInputStream = null;
		ArrayList<String> categoryList = null;
		try {
			// SO_REUSEADDR
			socketToServer = new Socket(serverIP, serverPort);
			// 
			outputStream = socketToServer.getOutputStream();
			objectOutputStream = new ObjectOutputStream(outputStream);
			inputStream = socketToServer.getInputStream();
			objectInputStream = new ObjectInputStream(inputStream);
			
			/**/
			/* reqCode | mode */
			Packet sendPacket = new Packet(CommandWord.REQUEST_CATEGORYLIST,mode);
			objectOutputStream.writeObject(sendPacket);
			
			/*categoryList*/
			Packet recvPacket = (Packet)objectInputStream.readObject();
			//CommandWord commandWord = recvPacket.getCommandWord();
			categoryList = (ArrayList<String>)recvPacket.getFields();
			
			for(int i = 0; i< categoryList.size();i++){
				String item = categoryList.get(i);
				SwingUtilities.invokeLater(new Runnable() {
					@Override
					public void run() {
						categoryListModel.addElement(item);
					}});
			}
			
		} catch (Exception e) {
			e.printStackTrace();
			SwingUtilities.invokeLater(new Runnable() {
				@Override
				public void run() {
					JOptionPane.showMessageDialog(null, "", "", JOptionPane.ERROR_MESSAGE);
				}
			});
			System.out.println(""+serverIP+serverPort);
		} finally {
			try {
				if(objectOutputStream !=null)objectOutputStream.close();
				if(objectInputStream != null) objectInputStream.close();
				if (socketToServer != null)socketToServer.close();
				System.out.println("");
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		return null;
	}// function call
}
