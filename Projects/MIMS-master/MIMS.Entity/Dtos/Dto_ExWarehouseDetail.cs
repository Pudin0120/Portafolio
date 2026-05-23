using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MIMS.Entity.Dtos
{
    public class Dto_ExWarehouseDetail
    {
        /// <summary>
        /// 
        /// </summary>		
        public int ID { get; set; }
        /// <summary>
        /// 
        /// </summary>		
        public string EWID { get; set; }
        /// <summary>
        /// 
        /// </summary>
        public int EWWay { get; set; }
        /// <summary>
        /// 
        /// </summary>
        public string Name { get; set; }
        /// <summary>
        /// 
        /// </summary>		
        public string PhaCode { get; set; }
        /// <summary>
        /// 
        /// </summary>
        public string PhaName { get; set; }
        /// <summary>
        /// 
        /// </summary>
        public string Spec { get; set; }
        /// <summary>
        /// 
        /// </summary>
        public string Unit { get; set; }
        /// <summary>
        /// 
        /// </summary>
        public string PinyinCode { get; set; }
        /// <summary>
        /// 
        /// </summary>		
        public int OrginID { get; set; }
        /// <summary>
        /// 
        /// </summary>		
        public string OrginName { get; set; }
        /// <summary>
        /// 
        /// </summary>		
        public double ExWarehouseNum { get; set; }
        /// <summary>
        /// 
        /// </summary>		
        public double Stock { get; set; }
        /// <summary>
        /// 
        /// </summary>		
        public int CompanyID { get; set; }
        /// <summary>
        /// 
        /// </summary>		
        public string CompanyName { get; set; }

        public string EWDate { get; set; }
    }
}
