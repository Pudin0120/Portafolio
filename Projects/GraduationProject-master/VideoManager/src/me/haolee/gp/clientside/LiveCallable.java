package me.haolee.gp.clientside;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import javax.swing.JOptionPane;
import me.haolee.gp.common.CommandWord;
import me.haolee.gp.common.Config;
import me.haolee.gp.common.Packet;
import me.haolee.gp.common.VideoInfo;

public class LiveCallable implements Callable<Integer> {
	
	/*
	 * call
	 * 
	 * */
	private String serverIP = null;
	private int serverPort = -1;
	/**/
	private VideoPanel selectedVideoPanel = null;
	
	/*SelectBlock*/
	public LiveCallable(VideoPanel selectedVideoPanel) {
		this.serverIP = Config.getValue("serverIP", "127.0.0.1");
		this.serverPort = Integer.valueOf(Config.getValue("serverPort", "10000"));
		this.selectedVideoPanel = selectedVideoPanel;
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
		
		VideoInfo videoInfo = null;//
		String fileRelativePath = null;//
		
		try {
			//
			// SO_REUSEADDR
			socketToServer = new Socket(serverIP, serverPort);
			// 
			outputStream = socketToServer.getOutputStream();
			objectOutputStream = new ObjectOutputStream(outputStream);
			inputStream = socketToServer.getInputStream();
			objectInputStream = new ObjectInputStream(inputStream);
			
			/*modecategory
			 * 
			 * +
			 * */
			/*+(+)*/
			videoInfo = selectedVideoPanel.getVideoInfo();//
			
			fileRelativePath = videoInfo.getFileRelativePath();//
			
			/*req|fileRelativePath
			 * ffmpeg
			 * */
			Packet sendPacket = new Packet(CommandWord.REQUEST_STREAMINGMEDIA,fileRelativePath);
			objectOutputStream.writeObject(sendPacket);
			
			//
			Packet recvPacket = null;
			recvPacket = (Packet)objectInputStream.readObject();
			/*
			 * FFmpeg
			 * 
			 * */
			if(recvPacket.getCommandWord() == CommandWord.RESPONSE_ABORT){
				System.out.println("");
				JOptionPane.showMessageDialog(null, "", "", JOptionPane.ERROR_MESSAGE);
				return null;
			}
			//
			String fileName = new File(fileRelativePath).getName();
			int dot = fileName.lastIndexOf(".");
			String fileID = fileName.substring(0, dot);
			//String rtspURL = "rtsp://"+serverIP+"/live/"+streamID;
			String rtspURL = "rtsp://"+serverIP+"/"+fileID+".sdp";
			Callable<Integer> callable = new Callable<Integer>() {
				@Override
				public Integer call() throws Exception {
					FFplay ffplay = new FFplay(rtspURL);
					ffplay.play();
					return null;
				}
			};
			Future<Integer> ffplayFuture = Executors.newSingleThreadExecutor().
					submit(callable);
			/*
			 * 
			 * */
			while(true){
				//
				recvPacket = (Packet)objectInputStream.readObject();
				//
				if(recvPacket.getCommandWord() == CommandWord.CTRL_HARTBEAT){
					//FFPLAY
					if(!ffplayFuture.isDone()){//ffplay
						sendPacket = new Packet(CommandWord.CTRL_HARTBEAT,null);
						objectOutputStream.writeObject(sendPacket);
					}else{//FFplayEND
						sendPacket = new Packet(CommandWord.CTRL_END,null);
						objectOutputStream.writeObject(sendPacket);
						break;//
					}
				}else{//CommandWord.CTRL_END
					break;//
				}
			}
			/*
			 * 
			 * 
			 */
			/*
			 * ffplay
			 * FFplayFFplayCallable
			 * ffplayFuture.get()
			 * 
			 * */
			/*
			 * call
			 * FFplayCallable
			 * */
			ffplayFuture.get();
			
		} catch (Exception e) {
			e.printStackTrace();
			JOptionPane.showMessageDialog(null, "", "", JOptionPane.ERROR_MESSAGE);
			System.out.println(""+serverIP+serverPort);
		} finally {
			try {
				if(objectInputStream!=null)objectInputStream.close();
				if(objectOutputStream!=null)objectOutputStream.close();
				if (socketToServer != null)socketToServer.close();
				System.out.println("");
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		return null;
	}// function call
}
