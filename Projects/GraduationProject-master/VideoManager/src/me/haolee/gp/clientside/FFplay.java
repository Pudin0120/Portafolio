package me.haolee.gp.clientside;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;

import javax.swing.JOptionPane;

class FFplay{

	private String rtspURL = null;
	public FFplay(String rtspUrl) {
		this.rtspURL = rtspUrl;
	}
	public void play() {
		//ffplay
		try {
			Process pc = null;
			ProcessBuilder pb = null;
			ArrayList<String> command = new ArrayList<>();//
			String os = System.getProperty("os.name");
			if(os.toLowerCase().startsWith("win")){
				File file = new File("ffplay.exe");//
				if(!file.exists()){
					JOptionPane.showMessageDialog(null, "ffplay.exe"
							, "", JOptionPane.ERROR_MESSAGE);
					return;
				}
				command.add("ffplay.exe");
			}
			else{//Linuxffplay
				command.add("ffplay");
			}
			//
			//rtspURLjava
			//
			//ffmpeg
			command.add(rtspURL);
			command.add("-x");
			command.add("1066");//
			command.add("-y");
			command.add("600");//

			pb = new ProcessBuilder(command);
			pb.redirectErrorStream(true);
			pc = pb.start();
			InputStream inputFFplayStatus = pc.getInputStream();
			BufferedReader readFFplayStatus = new BufferedReader(new InputStreamReader(inputFFplayStatus));
			
			try {
				while (readFFplayStatus.readLine() != null) {
					//System.out.println(tmp_in);//
				}
			} catch (Exception e) {e.printStackTrace();
			}finally {
				if(readFFplayStatus != null)readFFplayStatus.close();
				if (inputFFplayStatus != null)inputFFplayStatus.close();
				System.out.println("FFplay has finished");
			}
			/*
			 * FFplay
			 * FFplay
			 * */
			pc.waitFor();
			pc.destroy();
			
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
}