package me.haolee.gp.clientside;

import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import javax.swing.ButtonGroup;
import javax.swing.DefaultListModel;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JRadioButton;
import javax.swing.JScrollPane;
import javax.swing.JTextField;
import javax.swing.ListSelectionModel;
import javax.swing.SwingUtilities;
import javax.swing.UIManager;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import me.haolee.gp.common.CommandWord;
import me.haolee.gp.common.Config;

// main function
public class Client {
	private ExecutorService executorService = null;
	/*final*/
	private JFrame mainFrame = null;
	private JPanel mainPanel = null;//
	private JList<String> categoryList = null;
	private DefaultListModel<String> categoryListModel = null;
	private CommandWord mode = CommandWord.MODE_LIVE;//
	//
	private JLabel lblTotalNumber = null;
	//
	private int totalNumber = 0;
	//
	private int videoListStart = 0;//0
	private int videoListStep = 9;//
	
	private JTextField tfPageNo;
	
	public static void main(String[] args) {
		Client client = new Client();
		SwingUtilities.invokeLater(new Runnable() {
			@Override
			public void run() {
				client.createMainInterface();
			}
		});
	}// main

	// 
	public Client() {
		// create a ThreadPool
		this.executorService = Executors.newCachedThreadPool();
		//
		Config.readConfigFile("client.config");
	}

	// 
	private void createMainInterface() {
		int windowWidth = 1065;//
		int windowHeight = 650;//
		int mainPanelHeight = VideoPanel.getTotalHeight()+4*5;//5
		// user-interface
		try {
			UIManager.setLookAndFeel("com.sun.java.swing.plaf.nimbus.NimbusLookAndFeel");
		}catch (Exception e) {e.printStackTrace();}
		mainFrame = new JFrame("");
		mainFrame.setResizable(false);
		mainFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		mainFrame.setBounds(100, 0, windowWidth, windowHeight);
		
		/* frame */
		JPanel contentPane = new JPanel(null);//
		mainFrame.setContentPane(contentPane);
		/*
		 *      
		 * */
		/**/
		JMenuBar menuBar = new JMenuBar();
		menuBar.setBounds(0, 0, windowWidth, 25);//
		contentPane.add(menuBar);
		
		/**/
		JPanel upPanel = new JPanel();//
		/*  */
		contentPane.add(upPanel);
		upPanel.setBounds(0, 25, windowWidth, 40);//
		
		/**/
		JPanel downPanel = new JPanel();
		downPanel.setLayout(null);
		downPanel.setBounds(0, 565, windowWidth, 50);//
		contentPane.add(downPanel);
		
		/*,*/
		JScrollPane jScrollPane = new JScrollPane();
		/*  */
		contentPane.add(jScrollPane);
		/**/
		jScrollPane.setBounds(0, 65, windowWidth-4, 500);//
		
		/*
		 * 
		 * */
		mainPanel = new JPanel(new FlowLayout
				(FlowLayout.LEFT, 5, 5));/*5*/
		jScrollPane.setViewportView(mainPanel);//
		jScrollPane.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED);
		jScrollPane.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
		/**/
		mainPanel.setPreferredSize(new Dimension(windowWidth,mainPanelHeight));
		/**/
		ButtonGroup buttonGroup = new ButtonGroup();
		JRadioButton liveRButton = new JRadioButton("");
		liveRButton.setFont(new Font("Dialog", Font.BOLD, 15));
		liveRButton.setBounds(89, 5, 69, 30);
		JRadioButton vodRButton = new JRadioButton("");
		vodRButton.setFont(new Font("Dialog", Font.BOLD, 15));
		vodRButton.setBounds(19, 5, 66, 30);
		buttonGroup.add(liveRButton);
		upPanel.setLayout(null);
		buttonGroup.add(vodRButton);
		upPanel.add(vodRButton);
		upPanel.add(liveRButton);
		liveRButton.setSelected(true);
		
		/**/
		JLabel lblCategoryLabel = new JLabel("");
		lblCategoryLabel.setFont(new Font("Dialog", Font.BOLD, 15));
		lblCategoryLabel.setBounds(180, 5, 86, 30);
		upPanel.add(lblCategoryLabel);
		categoryListModel = new DefaultListModel<>();
		categoryList = new JList<>(categoryListModel);
		categoryList.setFont(new Font("Dialog", Font.BOLD, 20));
		categoryList.setBounds(270, 5, 600, 30);
		categoryList.setLayoutOrientation(JList.HORIZONTAL_WRAP);//
		categoryList.setVisibleRowCount(1);//
		categoryList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		upPanel.add(categoryList);
		
		/*
		 * 
		 * */
		getCategoryList();
		
		/*
		 * mainPanel
		 * contentPanecontentPane
		 * */
		//
		categoryList.addListSelectionListener(new ListSelectionListener() {
			public void valueChanged(ListSelectionEvent e) {
				/*
				 * http://stackoverflow.com/questions/12461627/jlist-fires-valuechanged-twice-when-a-value-is-changed-via-mouse
				 * valueChanged
				 * !e.getValueIsAdjusting()
				 * 
				 * !e.getValueIsAdjusting()
				 * categoryList.getSelectedValue
				 * */
				if(!e.getValueIsAdjusting() && categoryList.getSelectedValue()!=null){
					String selectedCategory = categoryList.getSelectedValue();//
					if(selectedCategory == null){//
						JOptionPane.showMessageDialog(null, ""
								, "", JOptionPane.INFORMATION_MESSAGE);
						return;
					}
					//
					TotalNumberCallable totalNumberCallable = new TotalNumberCallable(mode, selectedCategory);
					Future<Integer> future = executorService.submit(totalNumberCallable);
					try {
						totalNumber = future.get();
						int numberOfPages = (totalNumber-1)/videoListStep+1;//1
						lblTotalNumber.setText("/"+numberOfPages+"");
					} catch (Exception ex) {
						ex.printStackTrace();
					}
				}
			}
		});
		/*
		 * 
		 * */
		/*itemStateChanged
		 * */
		liveRButton.addItemListener(new ItemListener() {
			@Override
			public void itemStateChanged(ItemEvent e) {
				if(e.getStateChange() == ItemEvent.DESELECTED)//liveRButton
					mode = CommandWord.MODE_VOD;
				else								//liveRButton
					mode = CommandWord.MODE_LIVE;
				getCategoryList();//
			}
		});
		
		/*
		 * 
		 * */
		JButton btnRefreshVideoList = new JButton(new ImageIcon(((new ImageIcon(
	            "refresh.png").getImage().getScaledInstance(40, 40,
	                    java.awt.Image.SCALE_SMOOTH)))));
		btnRefreshVideoList.setBounds(900, 0, 40, 40);
		//btnRefreshVideoList.setContentAreaFilled(false);
		upPanel.add(btnRefreshVideoList);
		btnRefreshVideoList.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				/**/
				String selectedCategory = categoryList.getSelectedValue();//
				if(selectedCategory == null){//
					JOptionPane.showMessageDialog(null, ""
							, "", JOptionPane.INFORMATION_MESSAGE);
					return;
				}
				/**/
				mainPanel.removeAll();
				mainPanel.revalidate();
				mainPanel.repaint();
				
				/*""null*/
				SelectedVideoPanel.resetSelectedBlock();
				
				int currentPageNo = videoListStart/videoListStep+1;//1
				tfPageNo.setText(String.valueOf(currentPageNo));
				VideoListCallable videoListCallable = new VideoListCallable(mode
						, selectedCategory,videoListStart,videoListStep,mainPanel);
				executorService.submit(videoListCallable);
			}
		});

		/*
		 * 
		 * */
		JButton btnFirst = new JButton(new ImageIcon(((new ImageIcon(
	            "firstpage.png").getImage().getScaledInstance(35, 35,
	                    java.awt.Image.SCALE_SMOOTH)))));
		btnFirst.setBounds(205, 8, 35, 35);
		downPanel.add(btnFirst);
		btnFirst.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				/**/
				String selectedCategory = categoryList.getSelectedValue();//
				if(selectedCategory == null){//
					JOptionPane.showMessageDialog(null, ""
							, "", JOptionPane.INFORMATION_MESSAGE);
					return;
				}
				/**/
				mainPanel.removeAll();
				mainPanel.revalidate();
				mainPanel.repaint();
				/*""null*/
				SelectedVideoPanel.resetSelectedBlock();
				videoListStart = 0;//0
				int currentPageNo = videoListStart/videoListStep+1;//1
				tfPageNo.setText(String.valueOf(currentPageNo));
				
				VideoListCallable videoListCallable = new VideoListCallable(mode
						, selectedCategory,videoListStart,videoListStep,mainPanel);
				executorService.submit(videoListCallable);
			}
		});
		
		/*
		 * 
		 * */
		JButton btnLast = new JButton(new ImageIcon(((new ImageIcon(
	            "lastpage.png").getImage().getScaledInstance(35, 35,
	                    java.awt.Image.SCALE_SMOOTH)))));
		btnLast.setBounds(810, 8, 35, 35);
		downPanel.add(btnLast);
		btnLast.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				/**/
				String selectedCategory = categoryList.getSelectedValue();//
				if(selectedCategory == null){//
					JOptionPane.showMessageDialog(null, ""
							, "", JOptionPane.INFORMATION_MESSAGE);
					return;
				}
				/**/
				mainPanel.removeAll();
				mainPanel.revalidate();
				mainPanel.repaint();
				/*""null*/
				SelectedVideoPanel.resetSelectedBlock();
				
				//
				int numberOfPages = (totalNumber-1)/videoListStep+1;//
				videoListStart = (numberOfPages-1)*videoListStep;
				//
				int currentPageNo = videoListStart/videoListStep+1;//1
				tfPageNo.setText(String.valueOf(currentPageNo));
				
				VideoListCallable videoListCallable = new VideoListCallable(mode
						, selectedCategory,videoListStart,videoListStep,mainPanel);
				executorService.submit(videoListCallable);
			}
		});
		
		/*
		 * 
		 * */
		downPanel.setLayout(null);
		JButton btnPrevious = new JButton(new ImageIcon(((new ImageIcon(
	            "previouspage.gif").getImage().getScaledInstance(100, 35,
	                    java.awt.Image.SCALE_SMOOTH)))));
		btnPrevious.setBounds(320, 8, 100, 35);
		downPanel.add(btnPrevious);
		btnPrevious.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				/**/
				String selectedCategory = categoryList.getSelectedValue();//
				if(selectedCategory == null){//
					JOptionPane.showMessageDialog(null, ""
							, "", JOptionPane.INFORMATION_MESSAGE);
					return;
				}
				
				if(videoListStart == 0){
					JOptionPane.showMessageDialog(null, ""
							, "", JOptionPane.INFORMATION_MESSAGE);
					return;
				}else 
					;
				/**/
				mainPanel.removeAll();
				mainPanel.revalidate();
				mainPanel.repaint();
				
				/*""null*/
				SelectedVideoPanel.resetSelectedBlock();
				
				videoListStart -= videoListStep;//
				int currentPageNo = videoListStart/videoListStep+1;//1
				tfPageNo.setText(String.valueOf(currentPageNo));
				
				VideoListCallable videoListCallable = new VideoListCallable(mode
						, selectedCategory,videoListStart,videoListStep,mainPanel);
				executorService.submit(videoListCallable);
			}
		});
		
		
		/*
		 * 
		 * */
		JButton btnNext = new JButton(new ImageIcon(((new ImageIcon(
	            "nextpage.gif").getImage().getScaledInstance(100, 35,
	                    java.awt.Image.SCALE_SMOOTH)))));
		btnNext.setBounds(630, 8, 100, 35);
		downPanel.add(btnNext);
		btnNext.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				/**/
				String selectedCategory = categoryList.getSelectedValue();//
				if(selectedCategory == null){//
					JOptionPane.showMessageDialog(null, ""
							, "", JOptionPane.INFORMATION_MESSAGE);
					return;
				}
				
				if(videoListStart+videoListStep-1 >= totalNumber-1){
					JOptionPane.showMessageDialog(null, ""
							, "", JOptionPane.INFORMATION_MESSAGE);
					return;
				}else 
					;
				
				/**/
				mainPanel.removeAll();
				mainPanel.revalidate();
				mainPanel.repaint();
				
				/*""null*/
				SelectedVideoPanel.resetSelectedBlock();
				videoListStart += videoListStep;//
				int currentPageNo = videoListStart/videoListStep+1;//1
				tfPageNo.setText(String.valueOf(currentPageNo));
				
				VideoListCallable videoListCallable = new VideoListCallable(mode
						, selectedCategory,videoListStart,videoListStep,mainPanel);
				executorService.submit(videoListCallable);
			}
		});

		/*
		 * 
		 */
		JButton btnPlayVideo = new JButton(new ImageIcon(((new ImageIcon(
	            "play.png").getImage().getScaledInstance(50, 50,
	                    java.awt.Image.SCALE_SMOOTH)))));
		btnPlayVideo.setBounds(500, 0, 50, 50);
		//btnPlayVideo.setContentAreaFilled(false);
		downPanel.add(btnPlayVideo);
		btnPlayVideo.addActionListener(new ActionListener() {
		public void actionPerformed(ActionEvent e) {
			//
			VideoPanel selectedVideoPanel = SelectedVideoPanel.getSelectedVideoPanel();
			if(selectedVideoPanel == null){
				JOptionPane.showMessageDialog(null, ""
						, "", JOptionPane.INFORMATION_MESSAGE);
				return;
			}

			if(mode==CommandWord.MODE_VOD){
				VodCallable vodCallable = new VodCallable(selectedVideoPanel);
				executorService.submit(vodCallable);
			}
			else{//live
				LiveCallable liveCallable = new LiveCallable(selectedVideoPanel);
				executorService.submit(liveCallable);
			}
			
		}// actionPerformed
		});// addActionListener
		
		/*
		 * 
		 * */
		lblTotalNumber = new JLabel("/ ");
		lblTotalNumber.setFont(new Font("Dialog", Font.BOLD, 15));
		lblTotalNumber.setBounds(1000, 8, 50, 35);
		downPanel.add(lblTotalNumber);
		
		//
		JButton btnJumpPage = new JButton("");
		btnJumpPage.setFont(new Font("Dialog", Font.BOLD, 15));
		btnJumpPage.setBounds(890, 8, 66, 35);
		downPanel.add(btnJumpPage);
		
		//
		tfPageNo = new JTextField();
		tfPageNo.setFont(new Font("Dialog", Font.BOLD, 15));
		tfPageNo.setBounds(965, 8, 35, 35);
		downPanel.add(tfPageNo);
		tfPageNo.setColumns(10);
		
		btnJumpPage.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				/**/
				String selectedCategory = categoryList.getSelectedValue();//
				if(selectedCategory == null){//
					JOptionPane.showMessageDialog(null, ""
							, "", JOptionPane.INFORMATION_MESSAGE);
					return;
				}
				String pageNoText = tfPageNo.getText();
				if(pageNoText.equals("")){
					JOptionPane.showMessageDialog(null, ""
							, "", JOptionPane.INFORMATION_MESSAGE);
					return;
				}
				
				int pageNo = Integer.valueOf(pageNoText);
				//pageNonumberOfPages1
				int numberOfPages = (totalNumber-1)/videoListStep+1;//1
				if(pageNo > numberOfPages || pageNo < 1){
					JOptionPane.showMessageDialog(null, ""
							, "", JOptionPane.INFORMATION_MESSAGE);
					return;
				}
				
				/**/
				mainPanel.removeAll();
				mainPanel.revalidate();
				mainPanel.repaint();
				
				/*""null*/
				SelectedVideoPanel.resetSelectedBlock();
				
				videoListStart = (pageNo-1) * videoListStep;//
				VideoListCallable videoListCallable = new VideoListCallable(mode
						, selectedCategory,videoListStart,videoListStep,mainPanel);
				executorService.submit(videoListCallable);
			}
		});
		
		/*
		 * 
		 * */
		
		JMenu menuMain = new JMenu("");
		menuMain.setFont(new Font("Dialog", Font.BOLD, 18));
		menuBar.add(menuMain);
		
		JMenuItem menuItemExit = new JMenuItem("");
		menuItemExit.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				System.exit(0);
			}
		});
		menuItemExit.setFont(new Font("Dialog", Font.BOLD, 18));
		menuMain.add(menuItemExit);
		
		/*
		 * 
		 */
		mainFrame.setVisible(true);
	}// create

	//
	private void getCategoryList(){
		categoryListModel.removeAllElements();
		categoryList.revalidate();
		categoryList.repaint();
		CatagoryListCallable catagoryListCallable = new CatagoryListCallable(mode,categoryListModel);
		executorService.submit(catagoryListCallable);// 
	}
}// class