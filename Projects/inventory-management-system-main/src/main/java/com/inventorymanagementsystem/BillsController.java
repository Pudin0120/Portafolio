package com.inventorymanagementsystem;

import com.inventorymanagementsystem.config.Database;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import net.sf.jasperreports.engine.JasperCompileManager;
import net.sf.jasperreports.engine.JasperFillManager;
import net.sf.jasperreports.engine.JasperPrint;
import net.sf.jasperreports.engine.JasperReport;
import net.sf.jasperreports.engine.design.JRDesignQuery;
import net.sf.jasperreports.engine.design.JasperDesign;
import net.sf.jasperreports.engine.xml.JRXmlLoader;
import net.sf.jasperreports.view.JasperViewer;

import java.net.URL;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ResourceBundle;
import java.util.HashMap;
import java.util.Map;

public class BillsController implements Initializable {

    @FXML
    private Button bills_btn_print_bill;
    @FXML
    private TextField bills_search_invoice_number;
    @FXML
    private Button bills_btn_close;
    @FXML
    private AnchorPane bills_print_anchor_pane;

    private Connection connection;

    private Statement statement;

    private PreparedStatement preparedStatement;

    private ResultSet resultSet;


    public void onExit(){
        bills_btn_close.getScene().getWindow().hide();
    }

    public void searchAndPrintBillDetails() {
        String invoiceNumber = bills_search_invoice_number.getText() == null
                ? ""
                : bills_search_invoice_number.getText().trim();

        if (invoiceNumber.isEmpty()) {
            showInvoiceSearchError("Enter an invoice number before searching.");
            return;
        }

        try (Connection connection = Database.getInstance().connectDB()) {
            if (connection == null) {
                showInvoiceSearchError("The database connection is unavailable. Check the local database settings.");
                return;
            }

            String sql = "SELECT * FROM sales s "
                    + "INNER JOIN customers c ON s.cust_id = c.id "
                    + "WHERE s.inv_num = $P{INVOICE_NUMBER}";

            JasperDesign jasperDesign = JRXmlLoader.load(
                    getClass().getClassLoader().getResourceAsStream("jasper-reports/Invoice.jrxml"));
            JRDesignQuery query = new JRDesignQuery();
            query.setText(sql);
            jasperDesign.setQuery(query);

            JasperReport jasperReport = JasperCompileManager.compileReport(jasperDesign);
            Map<String, Object> parameters = new HashMap<>();
            parameters.put("INVOICE_NUMBER", invoiceNumber);

            JasperPrint jasperPrint = JasperFillManager.fillReport(
                    jasperReport, parameters, connection);
            JasperViewer.viewReport(jasperPrint, false);
        } catch (Exception exception) {
            showInvoiceSearchError("Unable to generate the invoice report. Check the invoice number and database.");
            exception.printStackTrace();
        }
    }

    private void showInvoiceSearchError(String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle("Invoice report");
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }

    @Override
    public void initialize(URL location, ResourceBundle resources) {
    }
}
