package me.haolee.gp.serverside;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import me.haolee.gp.common.Config;

public class Server {
	private int listeningPort = -1;//
	private ServerSocket serverSocket = null;
	private Socket socketToClient = null;
	private ExecutorService executorService = null;

	public static void main(String[] args) {
		// 
		Server server = new Server();
		server.startServer();
		server.listenAccept();
	}

	public void startServer() {
		try {
			// 
			executorService = Executors.newCachedThreadPool();
			/*
			 * 
			 * */
			Config.readConfigFile("server.config");
			
			/*keyvalue*/
			this.listeningPort = Integer.valueOf(
					Config.getValue("listeningPort","10000"));//
			
			serverSocket = new ServerSocket(listeningPort);// start
			
			System.out.println(" "+listeningPort+" ");
			//System.out.println("Server started... Listening port "+listeningPort);
		} catch (IOException e) {
			e.printStackTrace();
			try {
				if (serverSocket != null)
					serverSocket.close();
			} catch (IOException e2) {
				e2.printStackTrace();
			}
		}
	}// function startServer

	public void listenAccept() {
		while (true) {
			try {
				socketToClient = serverSocket.accept();
				executorService.submit(new RequestHandler(socketToClient));
			} catch (Exception e) {
				e.printStackTrace();
				System.out.println("Exception in listenAccept!");
			}

		} // while
	}// function listenAccept
}// class end
// 
