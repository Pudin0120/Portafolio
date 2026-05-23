using MIMS.Business;
using MIMS.IBusiness;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Linq;
using System.Web;
using System.Web.Mvc;

namespace MIMS.Web.Controllers
{
    public class SetupController : Controller
    {
        ICOM_UserBLL icom_userbll = new COM_UserBLL();
        // GET: Setup
        [RoleActionFilter]
        public ActionResult SqlConn()
        {
            ViewBag.connString = "DBMSSystem.Data.SqlClient<br/>localhost<br/>PharmacySystem";
            return View();
        }
        [RoleActionFilter]
        public ActionResult ModifyPsw()
        {
            return View();
        }
        [RoleActionFilter]
        public ActionResult Help()
        {
            return View();
        }
    }
}