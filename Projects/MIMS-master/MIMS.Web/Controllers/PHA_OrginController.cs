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
using System.Collections;

namespace MIMS.Web.Controllers
{
    public class PHA_OrginController : Controller
    {
        IPHA_OrginBLL ipha_orginbll = new PHA_OrginBLL();
        [RoleActionFilter]
        public ActionResult Index()
        {
            return View();
        }

        [HttpPost]
        public ActionResult LoadList(string rows, string page, string sort, string order, string query)
        {

            int count = default(int);
            IList list = ipha_orginbll.GetPageList(query, sort, order, int.Parse(page), int.Parse(rows), ref count);
            return Content(JsonConvert.SerializeObject(new
            {
                total = count,
                rows = list
            }));
        }

        [HttpPost]
        public ActionResult LoadForm(string id)
        {
            if (!string.IsNullOrEmpty(id))
                return Json(ipha_orginbll.GetEntity(id));
            else
                return null;

        }

        [HttpPost]
        public ActionResult AcceptClick(PHA_Orgin obj)
        {
            int isOk = default(int);
            //IDID0ID0ID
            if (obj.OrginID != 0)
                isOk = ipha_orginbll.Update(obj);
            else
                isOk = ipha_orginbll.Insert(obj);
            return Content(isOk.ToString());
        }

        [HttpPost]
        public ActionResult Del(string id)
        {
            if (!string.IsNullOrEmpty(id))
                return Content(ipha_orginbll.Delete(new PHA_Orgin { OrginID = int.Parse(id) }).ToString());
            else
                return null;
        }
    }
}