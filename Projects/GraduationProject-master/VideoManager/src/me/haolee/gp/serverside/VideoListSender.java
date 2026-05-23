package me.haolee.gp.serverside;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileInputStream;
import java.io.ObjectOutputStream;
import java.util.ArrayList;
import java.util.Iterator;

import javax.imageio.ImageIO;

import me.haolee.gp.common.CommandWord;
import me.haolee.gp.common.Config;
import me.haolee.gp.common.Packet;
import me.haolee.gp.common.VideoInfo;

public class VideoListSender {
	/*
	 * 
	 * */
	public void sendVideoList(CommandWord mode,String category,
			int videoListStart,int videoListStep,
			ObjectOutputStream objectOutputStream) {
		/* 
		 * DatebaseOperation
		 * */
		DatebaseQuery datebaseQuery = null;//
		/**/
		datebaseQuery = new DatebaseQuery();
		
		/*
		 * 
		 * */
		ArrayList<VideoInfo> videoInfoList=datebaseQuery.getVideoSet(mode, 
				category, videoListStart, videoListStep);
		/*
		 * videoInfobufferedImage*
		 * 
		 */
		//
		String pathPrefix = Config.getValue("pathPrefix"
				, "/home/mirage/EasyDarwin/Movies/");
		/**/
		String thumbnailRelativePath = Config.getValue(
				"thumbnailRelativePath","thumbnail/");//
		//
		try{
			//
			String thumbnailPath = null;
			for(int i = 0; i < videoInfoList.size(); i++){
				VideoInfo videoInfo = videoInfoList.get(i);
				//getName
				String fileName = new File(pathPrefix+videoInfo.getFileRelativePath()).getName();
				int dot = fileName.lastIndexOf(".");
				//
				String fileID = fileName.substring(0, dot);//0~dot-1
				
				thumbnailPath = pathPrefix+thumbnailRelativePath+fileID+".jpg";
				/**/
				BufferedImage bufferedImage = 
						ImageIO.read(new FileInputStream(thumbnailPath));
				/*videoInfo*/
				videoInfo.setBufferedImage(bufferedImage);//videoInfo
				/*videoInfo*/
				Packet sendPacket = new Packet(CommandWord.RESPONSE_DATA,videoInfo);
				objectOutputStream.writeObject(sendPacket);//
			}
			objectOutputStream.writeObject(new Packet(CommandWord.CTRL_END, null));
			
		}catch(Exception e){
			e.printStackTrace();
		}
	}
}
