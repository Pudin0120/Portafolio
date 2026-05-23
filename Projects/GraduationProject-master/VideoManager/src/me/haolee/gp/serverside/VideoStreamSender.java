package me.haolee.gp.serverside;

import java.io.File;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import me.haolee.gp.common.CommandWord;
import me.haolee.gp.common.Config;
import me.haolee.gp.common.Packet;

public class VideoStreamSender {
	/*
	 * 
	 * */
	public void sendVideoStream(String fileRelativePath,
			ObjectInputStream objectInputStream
			, ObjectOutputStream objectOutputStream) {

		try {
			
			//
			String pathPrefix = Config.getValue("pathPrefix", "/home/mirage/rtsp-relay/file/");
			//
			String fileAbsolutePath = pathPrefix + fileRelativePath;
			//getName
			String fileName = new File(fileAbsolutePath).getName();
			int dot = fileName.lastIndexOf(".");
			//
			String fileID = fileName.substring(0, dot);//0~dot-1
			//
			String fileExtension = fileName.substring(dot+1);

			StreamManager.generateStream(fileAbsolutePath);//
			//
			/*
			 * ID fileIDFFmpeg
			 * */
			Packet sendPacket = null;
			if (StreamManager.exists(fileID)) {
				sendPacket = new Packet(CommandWord.RESPONSE_CONTINUE,null);
				objectOutputStream.writeObject(sendPacket);
			} else {//
				sendPacket = new Packet(CommandWord.RESPONSE_ABORT,null);
				objectOutputStream.writeObject(sendPacket);
				return;
			}
			
			/*
			 * FFmpeg
			 * 
			 * */
			while(true){
				Thread.sleep(2000);
				//fileIDFFMPEG
				if(StreamManager.exists(fileID)){
					//send
					sendPacket = new Packet(CommandWord.CTRL_HARTBEAT,null);
					objectOutputStream.writeObject(sendPacket);
				}else{//FFMPEGEND
					sendPacket = new Packet(CommandWord.CTRL_END,null);
					objectOutputStream.writeObject(sendPacket);
					break;//
				}
				/*
				 * 
				 * 
				 * 
				 * */
				Packet recvPacket = (Packet)objectInputStream.readObject();
				if(recvPacket.getCommandWord() == CommandWord.CTRL_HARTBEAT)
					;
				else//CommandWord.CTRL_END 
					break;//
			}
			if(StreamManager.exists(fileID)){//FFmpegID
				StreamManager.releaseStream(fileID);
				System.out.println("Stream released");
			}
			else{ //FFmpegID
				StreamManager.removeStream(fileID);
				System.out.println("Stream removed");
			}
			
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}
