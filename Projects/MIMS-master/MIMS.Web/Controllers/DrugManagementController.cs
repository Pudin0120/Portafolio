using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;
using MIMS.IBusiness;
using MIMS.Business;
using MIMS.Entity;
using Newtonsoft.Json;
using System.Collections;
using MIMS.Entity.Model;

namespace MIMS.Web.Controllers
{
    public class DrugManagementController : Controller
    {
        IPHA_BaseInfoBLL ipha_baseinfobll = new PHA_BaseInfoBLL();
        IPHA_DosageFormBLL ipha_dosageformbll = new PHA_DosageFormBLL();
        IPHA_RepositoryBLL ipha_repositorybll = new PHA_RepositoryBLL();
        IPHA_StorageConditionBLL ipha_storageconditionbll = new PHA_StorageConditionBLL();
        IPHA_PhaAttrBLL ipha_phaattrbll = new PHA_PhaAttrBLL();
        IPHA_DispenseWayBLL ipha_dispensewaybll = new PHA_DispenseWayBLL();
        // GET: DrugManagement
        [RoleActionFilter]
        public ActionResult DrugInfo()
        {
            return View();
        }

        /// <summary>
        /// datagrid
        /// </summary>
        /// <param name="rows"></param>
        /// <param name="page"></param>
        /// <param name="sort"></param>
        /// <param name="order"></param>
        /// <param name="query"></param>
        /// <returns></returns>
        [HttpPost]
        public ActionResult LoadList(string rows, string page, string sort, string order, string query)
        {
            int count = default(int);
            IList list = ipha_baseinfobll.GetPageList(query, sort, order, int.Parse(page), int.Parse(rows), ref count);
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
                return Json(ipha_baseinfobll.GetEntity(id));
            else
                return null;
        }

        [HttpPost]
        public ActionResult LoadSelectDosageForm()
        {
            return Json(ipha_dosageformbll.GetList());
        }

        [HttpPost]

        public ActionResult LoadSelectRepo()
        {
            return Json(ipha_repositorybll.GetList());
        }

        [HttpPost]
        public ActionResult LoadSelectPhaAttr()
        {
            return Json(ipha_phaattrbll.GetList());
        }

        [HttpPost]
        public ActionResult LoadSelecSc()
        {
            return Json(ipha_storageconditionbll.GetList());
        }

        [HttpPost]
        public ActionResult LoadSelecDispenseWay()
        {
            return Json(ipha_dispensewaybll.GetList());
        }

        [HttpPost]
        public ActionResult AcceptClick(PHA_BaseInfo obj)
        {
            string key = Request["key"];
            int isOk = default(int);
            //key1 0
            if (key == "1")

                isOk = ipha_baseinfobll.Update(obj);
            else
            {
                PHA_BaseInfo temp = ipha_baseinfobll.GetEntity(obj.PhaCode);
                if (temp == null)
                    isOk = ipha_baseinfobll.Insert(obj);
                else
                    isOk = -1;         //
            }
            return Content(isOk.ToString());
        }

        [HttpPost]
        public ActionResult Del(string id)
        {
            if (!string.IsNullOrEmpty(id))
                return Content(ipha_baseinfobll.Delete(new PHA_BaseInfo { PhaCode = id }).ToString());
            else
                return null;
        }
    }
}