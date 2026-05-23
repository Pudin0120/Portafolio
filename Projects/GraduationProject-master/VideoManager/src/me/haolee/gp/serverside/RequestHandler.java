package me.haolee.gp.serverside;

import java.io.InputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.util.ArrayList;
import java.util.concurrent.Callable;

import me.haolee.gp.common.CommandWord;
import me.haolee.gp.common.Packet;

class RequestHandler implements Callable<Integer> {
	private Socket socketToClient = null;
	
	public RequestHandler(Socket s) {
		this.socketToClient = s;
	}

	@Override
	public Integer call() throws Exception {
		InputStream inputStream = null;
		OutputStream outputStream = null;
		ObjectInputStream objectInputStream = null;
		ObjectOutputStream objectOutputStream = null;//
		
		try {
			inputStream = socketToClient.getInputStream();
			objectInputStream = new ObjectInputStream(inputStream);
			outputStream = socketToClient.getOutputStream();
			objectOutputStream = new ObjectOutputStream(outputStream);
			
			// 	
			Packet recvPacket = (Packet)objectInputStream.readObject();
			CommandWord commandWord = recvPacket.getCommandWord();
			
			/**/
			
			CommandWord mode = null;
			String category = null;
			ArrayList<String> fields = null;
			Packet sendPacket = null;
			switch (commandWord) {
			case REQUEST_CATEGORYLIST:
				mode = (CommandWord)recvPacket.getFields();
				ArrayList<String> categoryList = new DatebaseQuery()
													.getCategoryList(mode);
				sendPacket = new Packet(CommandWord.RESPONSE_DATA,categoryList);
				objectOutputStream.writeObject(sendPacket);
				break;
			case REQUEST_TOTALNUMBER:
				fields = (ArrayList<String>)recvPacket.getFields();
				mode = CommandWord.valueOf(fields.get(0));
				category = (String)fields.get(1);
				int totalNumber = new DatebaseQuery().getTotalNumber(mode, category);
				sendPacket = new Packet(CommandWord.RESPONSE_DATA, totalNumber);
				objectOutputStream.writeObject(sendPacket);
				break;
			case REQUEST_VIDEOLIST:
				fields = (ArrayList<String>)recvPacket.getFields();
				mode = CommandWord.valueOf(fields.get(0));
				category = (String)fields.get(1);
				int videoListStart = Integer.valueOf(fields.get(2));
				int videoListStep = Integer.valueOf(fields.get(3));
				new VideoListSender().sendVideoList(mode, category, 
						videoListStart, videoListStep,
						objectOutputStream);
				break;
			case REQUEST_STREAMINGMEDIA:
				//filePath+
				//java
				String fileRelativePath = (String)recvPacket.getFields();
				new VideoStreamSender().sendVideoStream(fileRelativePath, 
						objectInputStream, objectOutputStream);
				break;
			default:
				System.out.println("Undefined Command: ");
				break;
			}
		System.out.println(commandWord+" ");
		} catch (Exception e) {
			e.printStackTrace();
			System.out.println("Client and its socket have exited!");
		} finally {
			try {
				if (objectOutputStream!=null)objectOutputStream.close();
				if (objectInputStream!=null)objectInputStream.close();
				if (inputStream != null)inputStream.close();
				if (outputStream != null)outputStream.close();
				if (socketToClient != null)socketToClient.close();
			} catch (Exception e2) {
				e2.printStackTrace();
			}
		} // catch-finally
		return null;
		
	}// function call
	

	/*
	 * 
	 * */
//	private BufferedImage generateThumbnail(String fileRelativePath) {
//		InputStream inputFromShell = null;//shell
//		BufferedImage bufferedImage =null;
//		Process pc = null;
//		ProcessBuilder pb = null;
//		try {
//			//filePath+
//			//java
//			String fileAbsolutePath  = pathPrefix + fileRelativePath;
//			ArrayList<String> command = new ArrayList<>();//
//			command.add("ffmpeg");
//			command.add("-y");
//			command.add("-i");
//			command.add(fileAbsolutePath);
//			command.add("-f");
//			command.add("mjpeg");
//			command.add("-t");
//			command.add("0.001");
//			command.add("-s");
//			command.add("320x240");
//			command.add("tmp.jpg");
//			//String[] cmd = { "sh", "-c", "ffmpeg -y -i "+ "\"" +fileAbsolutePath+"\""+" -f mjpeg -t 0.001 -s 320x240 tmp.jpg" };
//			pb = new ProcessBuilder(command);
//			pb.redirectErrorStream(true);
//			pc = pb.start();
//			inputFromShell = pc.getInputStream();
//			BufferedReader readFromShell = new BufferedReader(new InputStreamReader(inputFromShell));
//			String tmp_in = null;
//			try {
//				while ((tmp_in = readFromShell.readLine()) != null) {
//					System.out.println(tmp_in);
//				}
//			} catch (Exception e) {e.printStackTrace();}
//			pc.destroy();
//			bufferedImage = ImageIO.read(new FileInputStream("tmp.jpg"));
//			File file = new File("tmp.jpg");
//			if(file.exists())file.delete();
//		} catch (Exception e) {
//			e.printStackTrace();
//		} finally {
//			try {
//				if (inputFromShell != null)inputFromShell.close();
//			} catch (IOException e) {
//				e.printStackTrace();
//			}
//		} // finally
//		return bufferedImage;
//	}
	
}// class end