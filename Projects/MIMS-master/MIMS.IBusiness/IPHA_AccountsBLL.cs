using MIMS.Entity.Model;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MIMS.IBusiness
{
    public interface IPHA_AccountsBLL
    {
        /// <summary>
        /// 
        /// </summary>
        /// <param name="query"></param>
        /// <param name="orderField"></param>
        /// <param name="orderType"></param>
        /// <param name="pageIndex"></param>
        /// <param name="pageSize"></param>
        /// <param name="count"></param>
        /// <returns></returns>
        IList GetPageList(Hashtable ht, string orderField, string orderType, int pageIndex, int pageSize, ref int count);
        /// <summary>
        /// 
        /// </summary>
        /// <param name="id"></param>
        /// <returns></returns>
        PHA_Accounts GetEntity(string phaCode, string orginID);
        int Update(PHA_Accounts obj);
        int Delete(PHA_Accounts obj);
        int Insert(PHA_Accounts obj);
    }
}
