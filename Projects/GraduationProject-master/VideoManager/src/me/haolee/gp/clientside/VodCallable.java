package me.haolee.gp.clientside;

import java.util.concurrent.Callable;
import javax.swing.JOptionPane;

import me.haolee.gp.common.Config;
import me.haolee.gp.common.VideoInfo;

public class VodCallable implements Callable<Integer>{
	
	/*
	 * call
	 * 
	 * */
	private String serverIP = null;
	private int serverPort = -1;
	/**/
	private VideoPanel selectedVideoPanel = null;

	public VodCallable(VideoPanel selectedVideoPanel) {
		this.serverIP = Config.getValue("serverIP", "127.0.0.1");
		this.serverPort = Integer.valueOf(Config.getValue("serverPort", "10000"));
		this.selectedVideoPanel = selectedVideoPanel;
	}


	@Override
	public Integer call() throws Exception {
		VideoInfo videoInfo = null;//
		String fileRelativePath = null;//
		
		try {
			//server
			/**/

			videoInfo = selectedVideoPanel.getVideoInfo();//
			
			fileRelativePath = videoInfo.getFileRelativePath();//
//			String rtspURL = "rtsp://"
//					+serverIP+"/file/"+fileRelativePath;
			String rtspURL = "rtsp://"+serverIP+"/"+fileRelativePath;
			FFplay ffplay = new FFplay(rtspURL);
			ffplay.play();
			
		} catch (Exception e) {
			e.printStackTrace();
			JOptionPane.showMessageDialog(null, "", "", JOptionPane.ERROR_MESSAGE);
			System.out.println(""+serverIP+serverPort);
		} finally {
			System.out.println("");
		}
		return null;
	}// function call
}
