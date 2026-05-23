package me.haolee.gp.serverside;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class StreamManager {
	private static ConcurrentHashMap<String, Integer> streamIDRefCounter = new ConcurrentHashMap<>();
	private static ExecutorService executorService = Executors.newCachedThreadPool();
	
	public synchronized static void generateStream(String fileAbsolutePath) {
		
		String fileName = new File(fileAbsolutePath).getName();
		int dot = fileName.lastIndexOf(".");
		String streamID = fileName.substring(0, dot);
		
		if(exists(streamID)){//fileID1
			int refCounter = streamIDRefCounter.get(streamID);
			refCounter++;
			streamIDRefCounter.put(streamID, refCounter);
			
		}else{//
			FFmpegCallable ffmpegCallable = new FFmpegCallable(fileAbsolutePath);
			executorService.submit(ffmpegCallable);
			streamIDRefCounter.put(streamID, 1);
		}
		
	}
	public static boolean exists(String streamID) {
		if(streamIDRefCounter.containsKey(streamID))
			return true;
		else 
			return false;
	}
	//ffmpegfileID
	public synchronized static void removeStream(String streamID) {
		streamIDRefCounter.remove(streamID);
	}
	//ID10
	//ffmpegstreamRefCounter
	public synchronized static void releaseStream(String streamID) {
		int refCounter = streamIDRefCounter.get(streamID);
		refCounter --;
		if(refCounter != 0)//fileID
			streamIDRefCounter.put(streamID, refCounter);
		else{//
			InputStream inputFromShell = null;
			try {
			    Process pc = null;
			    ProcessBuilder pb = null;
			    String[] command = { "sh", "-c", "ps aux | grep ffmpeg |grep " + streamID + " | grep -v grep | awk '{print $2}' | xargs kill -9"};
			    pb = new ProcessBuilder(command);
			    pb.redirectErrorStream(true);
			    pc = pb.start();
			    inputFromShell = pc.getInputStream();
			    BufferedReader inFromShell = new BufferedReader(new InputStreamReader(inputFromShell));
			    String tmp_in = null;
			    while ((tmp_in = inFromShell.readLine()) != null)
			        System.out.println(tmp_in);
			    pc.waitFor();
			    pc.destroy();
			} catch (Exception e) {
			    e.printStackTrace();
			}
			finally {
			    try {
			        if (inputFromShell != null)inputFromShell.close();
			        System.out.println("Shell ffmpeg has been killed");
			    } catch (IOException e) {
			        e.printStackTrace();
			    }
			}
			streamIDRefCounter.remove(streamID);//
		}
	}
}

class FFmpegCallable implements Callable<Integer>{
	String fileAbsolutePath = null;
	public FFmpegCallable(String fileAbsolutePath) {
		this.fileAbsolutePath = fileAbsolutePath;
	}
	@Override
	public Integer call() throws Exception {
		
		InputStream inputFromShell = null;//shell
		Process pc = null;
		ProcessBuilder pb = null;
		
		String fileName = new File(fileAbsolutePath).getName();
		int dot = fileName.lastIndexOf(".");
		String fileID = fileName.substring(0, dot);
		String fileExtension = fileName.substring(dot+1);
		
		ArrayList<String> command = new ArrayList<>();//
		command.add("ffmpeg");
		
		//live()
		if(fileExtension.equals("live")){
			InputStream fileInputStream = new FileInputStream(fileAbsolutePath);
			String cameraURL = new BufferedReader(new InputStreamReader(fileInputStream)).readLine();
			fileInputStream.close();
			command.add("-i");
			command.add(cameraURL);
		}else{//
			command.add("-re");
			command.add("-i");
			command.add(fileAbsolutePath);
			command.add("-c");
			command.add("copy");
		}
		
		command.add("-f");
		command.add("rtsp");
		command.add("rtsp://"+"127.0.0.1"+"/"+fileID+".sdp");
		pb = new ProcessBuilder(command);
		pb.redirectErrorStream(true);
		pc = pb.start();
		inputFromShell = pc.getInputStream();
		BufferedReader readFromShell = new BufferedReader(new InputStreamReader(inputFromShell));
		String tmp_in = null;
		while((tmp_in = readFromShell.readLine()) != null){
			//System.out.println(tmp_in);
		}
		pc.destroy();
		System.out.println("FFmpeg stoped");
		StreamManager.removeStream(fileID);//fileID
		return null;
	}
}