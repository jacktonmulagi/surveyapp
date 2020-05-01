package sms;


import com.africastalking.AfricasTalking;
import com.africastalking.SmsService;
import com.africastalking.sms.Recipient;

import java.sql.*;
import java.util.Calendar;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

class sms extends TimerTask
{
    public static final String USERNAME = "esurvey";
    public static final String API_KEY = "de8fbaad2b31fde57ec236a23f26c679c7d63e4eb0c6973db514373912bfec39";

    public static void main(String[] args)


    {Timer timer = new Timer();
        timer.schedule(new sms(), 0, 60000);
        try
        {
            // create our mysql database connection
            String myDriver = "com.mysql.jdbc.Driver";
            String myUrl = "jdbc:mysql://localhost/bulksms";
            Class.forName(myDriver);
            Connection conn = DriverManager.getConnection(myUrl, "root", "");

            // our SQL SELECT query.
            // if you only need a few columns, specify them by name instead of using "*"
            String query = "SELECT o.text, p.phoneNo FROM sendingsms o, phoneno p WHERE p.username = o.username";

            // create the java statement
            Statement st = conn.createStatement();

            // execute the query, and get a java resultset
            ResultSet rs = st.executeQuery(query);

            // iterate through the java resultset
            while (rs.next())
            {
                String text = rs.getString("text");
                String peopele = rs.getString("phoneNo");


                // print the results
                System.out.print( "this is the numner:"+peopele +text);






                /* Initialize SDK */
                AfricasTalking.initialize(USERNAME, API_KEY);

                /* Get the SMS service */
                SmsService sms = AfricasTalking.getService(AfricasTalking.SERVICE_SMS);

                /* Set the numbers you want to send to in international format */
                String recipients = rs.getString("phoneNo");;

                /* Set your message */
                String message = rs.getString("text");;

                /* Set your shortCode or senderId */


                /* That’s it, hit send and we’ll take care of the rest */

                try {
                    List<Recipient> response = sms.send(message, new String[]{recipients}, true);

                    for (Recipient recipient : response) {
                        System.out.print(recipient.number);
                        System.out.print(" : ");
                        System.out.println(recipient.status);
                        System.out.println(recipient.cost);
                        System.out.println(recipient.messageId);
                        try
                        {
                            // create a mysql database connection
                            String myDriver1 = "com.mysql.jdbc.Driver";
                            String myUrl1 = "jdbc:mysql://localhost/bulksms";
                            Class.forName(myDriver1);
                            Connection conn1 = DriverManager.getConnection(myUrl1, "root", "");
                            /* Initialize SDK */

                            Calendar calendar = Calendar.getInstance();
                            java.sql.Date startDate = new java.sql.Date(calendar.getTime().getTime());

                            // the mysql insert statement
                            String query1 = " insert into deliveryreport (Time, to_number,cost, status)"
                                    + " values (?, ?,?, ?)";

                            // create the mysql insert preparedstatement
                            PreparedStatement preparedStmt = conn1.prepareStatement(query1);
                            preparedStmt.setDate   (1, startDate);
                            preparedStmt.setString (2, recipient.number);
                            preparedStmt.setString (3, recipient.cost);
                            preparedStmt.setString (4, recipient.status);



                            // execute the preparedstatement
                            preparedStmt.execute();

                            conn1.close();


                        }
                        catch (Exception e)
                        {
                            System.err.println("Got an exception!");
                            System.err.println(e.getMessage());
                        }

                        try
                        {
                            // create a mysql database connection
                            String myDriver1 = "com.mysql.jdbc.Driver";
                            String myUrl1 = "jdbc:mysql://localhost/bulksms";
                            Class.forName(myDriver1);
                            Connection conn1 = DriverManager.getConnection(myUrl1, "root", "");
                            /* Initialize SDK */

                            Calendar calendar = Calendar.getInstance();
                            java.sql.Date startDate = new java.sql.Date(calendar.getTime().getTime());

                            // the mysql insert statement
                            String query1 = " TRUNCATE sendingsms";

                            // create the mysql insert preparedstatement
                            PreparedStatement preparedStmt = conn1.prepareStatement(query1);




                            // execute the preparedstatement
                            preparedStmt.execute();

                            conn1.close();


                        }
                        catch (Exception e)
                        {
                            System.err.println("Got an exception!");
                            System.err.println(e.getMessage());
                        }




                    }


                } catch(Exception ex) {
                    ex.printStackTrace();
                }
            }
            st.close();
        }
        catch (Exception e)
        {
            System.err.println("Got an exception! ");
            System.err.println(e.getMessage());
        }




            }




    @Override
    public void run() {

    }
}
