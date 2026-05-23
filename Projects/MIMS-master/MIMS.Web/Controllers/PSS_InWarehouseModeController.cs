using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;
using MIMS.IBusiness;
using MIMS.Business;
using MIMS.Entity;
using Newtonsoft.Json;
using MIMS.Entity.Model;

namespace MIMS.Web.Controllers
{
    public class PSS_InWarehouseModeController : Controller
    {
        IPSS_InWarehouseModeBLL ipss_inwarehousemodebll = new PSS_InWarehouseModeBLL();
        // GET: BaseInfoMaintenance
        [RoleActionFilter]
        public ActionResult Index()
        {
            return View();
        }

        [HttpPost]
        public ActionResult LoadList()
        {
            return Json(ipss_inwarehousemodebll.GetList());
        }

        [HttpPost]
        public ActionResult LoadForm(string id)
        {
            if (!string.IsNullOrEmpty(id))
                return Json(ipss_inwarehousemodebll.GetEntity(id));
            else
                return null;

        }

        [HttpPost]
        public ActionResult AcceptClick(PSS_InWarehouseMode obj)
        {
            int isOk = default(int);
            //IDID0ID0ID
            if (obj.ID != 0)
                isOk = ipss_inwarehousemodebll.Update(obj);
            else
                isOk = ipss_inwarehousemodebll.Insert(obj);
            return Content(isOk.ToString());
        }

        [HttpPost]
        public ActionResult Del(string id)
        {
            if (!string.IsNullOrEmpty(id))
                return Content(ipss_inwarehousemodebll.Delete(new PSS_InWarehouseMode { ID = int.Parse(id) }).ToString());
            else
                return null;
        }
    }
}