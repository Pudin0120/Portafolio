package me.haolee.gp.clientside;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;

import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.border.EmptyBorder;

import me.haolee.gp.common.*;

import java.awt.Graphics;
import java.awt.GridLayout;
import java.awt.Image;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.image.BufferedImage;

/*

               + <-------+width+2*padding+------> +----+
               |                                       |
          +-+------------------------------------------+
            ^  |               padding                 |
            |  |  +--------------------------------+   |
            |  |p |                                |   |
            +  |a |                                |   |
height+        |d |                                |   |
2*padding+     |d |                                |   |
infoAreaHeight |i |                                |   |
               |n |                                |   |
            +  |g |                                |   |
            |  |  |                                |   |
            |  |  +--------------------------------+   |
            v  |                                       |
               |                                       |
          +----+---------------------------------------+


 * 
 * */
class VideoPanel extends JPanel{

	private static final long serialVersionUID = 5857923303664996266L;
	/**
	 * 
	 */
	private int tnWidth = 320, tnHeight = 240;//
	private int blockWidth = -1,blockHeight  = -1;//DisplayBlock
	private int padding = 10;//
	private int infoHeight = 50;//
	private VideoInfo videoInfo = null;
	//,
	public static int getTotalHeight() {
		//blockHeight = tnHeight+3*padding+infoHeight;
		return 3*(240+3*10+50);//33
	}
	//videoInfo
	public VideoInfo getVideoInfo() {
		return videoInfo;
	}
	//HashMap<>()
	public VideoPanel(VideoInfo videoInfo) {
		
		this.videoInfo = videoInfo;
		//DisplayBlock
		blockWidth = tnWidth+2*padding;
		blockHeight = tnHeight+3*padding+infoHeight;
		this.setPreferredSize(new Dimension(blockWidth,blockHeight));//padding
		this.setBackground(SelectedVideoPanel.getNoSelectionColor());//
		this.setLayout(null);//
		//
		this.addMouseListener(new MouseAdapter() {
			@Override
			public void mouseClicked(MouseEvent e) {
				super.mouseClicked(e);
				System.out.println("Click");
				//
				VideoPanel thisDisplayBlock = (VideoPanel)e.getSource();
				SelectedVideoPanel.changeSelectionBlock(thisDisplayBlock);//
			}
		});
		BufferedImage bufferedImage = videoInfo.getBufferedImage();
		//
		ThumbnailPanel thumbnailPanel = new ThumbnailPanel(tnWidth,tnHeight,bufferedImage);
		thumbnailPanel.repaint();//
		this.add(thumbnailPanel);//
		thumbnailPanel.setBounds(padding,padding, tnWidth,tnHeight);//,
		//
		InfoPanel infoPanel = new InfoPanel(
				videoInfo.getVideoName(),
				videoInfo.getDuration(),
				videoInfo.getResolution());
		this.add(infoPanel);
		infoPanel.setBounds(padding, tnHeight+2*padding, tnWidth,infoHeight);//,
		//thumbnailPanelinfoPanel
		JPanel gapPanel = new JPanel();
		gapPanel.setBackground(new Color(166, 166, 166));
		this.add(gapPanel);
		gapPanel.setBounds(padding, tnHeight+padding, tnWidth, padding);
	}
}

/*
 * 
 * */
class ThumbnailPanel extends JPanel{
	
	/**
	 * 
	 */
	private static final long serialVersionUID = 2070125390008961705L;
	private Image scaledImage = null;
	//
	public ThumbnailPanel(int tnWidth , int tnHeight, BufferedImage bufferedImage) {
		this.scaledImage = bufferedImage.getScaledInstance(tnWidth, tnHeight, Image.SCALE_DEFAULT);
	}
	
	/*
	 * getGraphicsGraphicsdrawImagegetGraphicsnull
	 * paintCommonentrepaint
	 * http://stackoverflow.com/questions/23717634/nullpointerexception-when-calling-graphics-drawimage/23717710#23717710
	 * http://stackoverflow.com/questions/15986677/drawing-an-object-using-getgraphics-without-extending-jframe/15991175#15991175
	 * */
	@Override
	protected void paintComponent(Graphics g) {
		super.paintComponent(g);
		g.drawImage(scaledImage, 0, 0, this);
	}
}

/**/
class InfoPanel extends JPanel{

	/**
	 * 
	 */
	private static final long serialVersionUID = 2611671258325196571L;

	public InfoPanel(String videoName,String duration,String resolution) {
		this.setBackground(new Color(196,196,196));
		//this.setLayout(new GridLayout(3, 1, 0, 3));//   
		this.setLayout(null);
		JLabel jLabelVideoName = new JLabel(""+videoName);
		JLabel jLabelDuration = new JLabel(""+duration);
		JLabel jLabelResolution = new JLabel(""+resolution);
		jLabelVideoName.setFont(new Font("Dialog", Font.BOLD, 15));
		jLabelDuration.setFont(new Font("Dialog", Font.BOLD, 15));
		jLabelResolution.setFont(new Font("Dialog", Font.BOLD, 15));
		this.add(jLabelVideoName);
		this.add(jLabelDuration);
		this.add(jLabelResolution);
		//50.320
		jLabelVideoName.setBounds(2, 2, 320, 15);
		jLabelDuration.setBounds(2, 18, 320, 15);
		jLabelResolution.setBounds(2, 34, 320, 15);
	}
}


/**/
class SelectedVideoPanel{
	private static VideoPanel selectedVideoPanel = null;//
	private static Color noSelectionColor = new Color(184,184,184);//
	private static Color selectionColor = new Color(137,186,251);//
	/**/
	public static VideoPanel getSelectedVideoPanel() {
		return selectedVideoPanel;
	}
	public static void changeSelectionBlock(VideoPanel videoPanel) {
		if(selectedVideoPanel != null)//
			selectedVideoPanel.setBackground(noSelectionColor);//
		videoPanel.setBackground(selectionColor);//
		selectedVideoPanel = videoPanel;//
	}
	public static Color getNoSelectionColor() {
		return noSelectionColor;
	}
	/**
	 * lastBlockNull
	 */
	public static void resetSelectedBlock() {
		selectedVideoPanel = null;
	}
}