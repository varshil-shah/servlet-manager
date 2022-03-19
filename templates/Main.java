import jakarta.servlet.*;

import jakarta.servlet.http.*;

import java.io.*;

public class Main extends HttpServlet {

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {

        response.setContentType("text/html");

        final PrintWriter out = response.getWriter();
        out.println("<html>");
        out.println("<head><title>The GET method</title></head>");
        out.println("<body>");
        out.println("The servlet has received a GET. Now, click the button below.");
        out.println("<br>");
        out.println("<form method=\"post\">");
        out.println("<input type=\"submit\" value=\"Submit\">");
        out.println("</form></body></html>");

    }

    public void doPost( HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {

        response.setContentType("text/html");

        final PrintWriter out = response.getWriter();
        out.println("<html>");
        out.println("<head>");
        out.println("<title>The POST method</title>");
        out.println("</head>");
        out.println("<body>");
        out.println("The servlet has received a POST. Thank you.");
        out.println("</body>");
        out.println("</html>");
    }

}
