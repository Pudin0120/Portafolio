using System;
using System.Collections.Generic;
using System.Collections;
using System.Linq;
using System.Web;
using System.Web.Mvc;
using MIMS.IBusiness;
using MIMS.Business;
using MIMS.Entity;
using Newtonsoft.Json;
using MIMS.Entity.Model;
using MIMS.Entity.Dtos;

namespace MIMS.Web.Controllers
{
    public class PSS_InWarehouseController : Controller
    {
        IPSS_InWarehouseBLL ipss_inwarehousebll = new PSS_InWarehouseBLL();
        IPSS_InWarehouseDetailBLL ipss_inwarehousedetailbll = new PSS_InWarehouseDetailBLL();
        IPSS_InWarehouseModeBLL ipss_inwarehousemodebll = new PSS_InWarehouseModeBLL();
        IPHA_AccountsBLL ipha_accountsbll = new PHA_AccountsBLL();

        // GET: PSS_InWarehouse
        [RoleActionFilter]
        public ActionResult InWarehouse()
        {
            return View();
        }
        [HttpPost]
        public ActionResult LoadList()
        {
            return Json(ipss_inwarehousebll.GetList());
        }

        [HttpPost]
        public ActionResult LoadForm(string id)
        {
            if (!string.IsNullOrEmpty(id))
                return Json(ipss_inwarehousebll.GetEntity(id));
            else
                return null;
        }

        [HttpPost]
        public ActionResult AcceptClick(PSS_InWarehouse obj)
        {
            string key = Request["key"];
            int old_isiw = default(int);
            int.TryParse(Request["old_isiw"], out old_isiw);
            int isOk = default(int);
            //key1 0
            if (key == "1")
            {
                //
                if (obj.IsIW == 1 && old_isiw == 0)
                {
                    //
                    obj.IWDate = DateTime.Now.ToString("G");
                    //
                    Hashtable ht = new Hashtable();
                    ht.Add("IWID", obj.IWID);
                    IList list = ipss_inwarehousedetailbll.GetList(ht);
                    //
                    foreach (Dto_InWarehouseDetail item in list)
                    {
                        PHA_Accounts a = ipha_accountsbll.GetEntity(item.PhaCode, item.OrginID.ToString());
                        a.Stock += item.InWarehouseCount;
                        ipha_accountsbll.Update(a);
                    }
                }
                isOk = ipss_inwarehousebll.Update(obj);
            }
            else
            {
                PSS_InWarehouse temp = ipss_inwarehousebll.GetEntity(obj.IWID.ToString());
                if (temp == null)
                {
                    HttpCookie cookie = Request.Cookies["user"];
                    obj.OperateNo = cookie.Values["Code"];
                    obj.OperateDate = DateTime.Now.ToString("G");
                    isOk = ipss_inwarehousebll.Insert(obj);
                }
                else
                    isOk = -1;
            }
            return Content(isOk.ToString());
        }

        [HttpPost]
        public ActionResult Del(string id)
        {
            if (!string.IsNullOrEmpty(id))
                return Content(ipss_inwarehousebll.Delete(new PSS_InWarehouse { IWID = id }).ToString());
            else
                return null;
        }

        [HttpPost]
        public ActionResult LoadSelectInwarehourseMode()
        {
            return Json(ipss_inwarehousemodebll.GetList());
        }
    }
}