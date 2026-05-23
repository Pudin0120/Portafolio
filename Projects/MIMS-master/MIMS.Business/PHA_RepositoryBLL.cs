using MIMS.IBusiness;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Collections;
using MIMS.Service;
using MIMS.Entity.Model;


namespace MIMS.Business
{
    public class PHA_RepositoryBLL:IPHA_RepositoryBLL
    {
        private static readonly PHA_RepositoryDAL dal = new PHA_RepositoryDAL();
        /// <summary>
        /// list
        /// </summary>
        /// <returns></returns>
        public IList GetList()
        {
            return dal.GetList();
        }
        /// <summary>
        /// 
        /// </summary>
        /// <param name="id"></param>
        /// <returns></returns>
        public PHA_Repository GetEntity(string id)
        {
            return dal.GetEntity(id);
        }


        public int Update(PHA_Repository obj)
        {
            return dal.Update(obj);
        }
        public int Insert(PHA_Repository obj)
        {
            return dal.Insert(obj);
        }


        public int Delete(PHA_Repository obj)
        {
            return dal.Delete(obj);
        }
    }
}
