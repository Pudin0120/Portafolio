using System;
using System.Collections;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Data.SqlClient;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Dapper;
using MIMS.Entity.Model;

namespace MIMS.Service
{
    public class PHA_AccountsDAL
    {
        #region init dbconnection
        private static readonly string connString = ConfigurationManager.ConnectionStrings["PharmacySystem"].ConnectionString;
        private IDbConnection _conn;
        public IDbConnection Conn
        {
            get
            {
                _conn = new SqlConnection(connString);
                _conn.Open();
                return _conn;
            }
        }
        #endregion

        public IList<PHA_Accounts> GetList()
        {
            using (Conn)
            {
                string query = "SELECT top 100 * FROM PHA_Accounts";
                return Conn.Query<PHA_Accounts>(query).ToList();
            }

        }
        /// <summary>
        /// ()
        /// </summary>
        /// <param name="where"></param>
        /// <param name="orderField"></param>
        /// <param name="prams"></param>
        /// <param name="orderType"></param>
        /// <param name="pageIndex"></param>
        /// <param name="pageSize"></param>
        /// <param name="count"></param>
        /// <returns></returns>
        public IList GetPageListWhere(StringBuilder where, Dictionary<string, object> prams, string orderField, string orderType, int pageIndex, int pageSize, ref int count)
        {
            int num = (pageIndex - 1) * pageSize;
            int num1 = pageIndex * pageSize;
            using (Conn)
            {
                StringBuilder strSql = new StringBuilder();
                StringBuilder sql = new StringBuilder();
                sql.Append(@"SELECT * FROM (SELECT  A.*,
                                                    B.PhaName,
                                                    B.Spec,
                                                    B.Unit,
                                                    B.PinyinCode,
                                                    O.OrginName,
                                                    C.CompanyName
                                                     FROM PHA_Accounts A
                                                    LEFT JOIN PHA_BaseInfo B ON A.PhaCode = B.PhaCode
                                                    LEFT JOIN PHA_Orgin O ON A.OrginID = O.OrginID
                                                    LEFT JOIN PSS_PurchaseCompany C ON A.CompanyID = C.CompanyID) A WHERE 1=1 ");
                sql.Append(where);
                strSql.Append("Select * From (Select ROW_NUMBER() Over (Order By " + orderField + " " + orderType + "");
                strSql.Append(") As rowNum, * From (" + sql + ") As T ) As N Where rowNum > " + num + " And rowNum <= " + num1 + "");
                count = Conn.Query<int>("Select Count(1) From (" + sql + ") As t", prams).Single();
                return Conn.Query<PHA_Accounts>(strSql.ToString(), prams).ToList();
            }

        }
        /// <summary>
        /// 
        /// </summary>
        /// <param name="id"></param>
        /// <returns></returns>
        public PHA_Accounts GetEntity(string phaCode, string orginID)
        {
            using (Conn)
            {
                string query = @"SELECT * FROM (SELECT  A.*,
                                                    B.PhaName,
                                                    B.Spec,
                                                    B.Unit,
                                                    B.PinyinCode,
                                                    O.OrginName,
                                                    C.CompanyName
                                                     FROM PHA_Accounts A
                                                    LEFT JOIN PHA_BaseInfo B ON A.PhaCode = B.PhaCode
                                                    LEFT JOIN PHA_Orgin O ON A.OrginID = O.OrginID
                                                    LEFT JOIN PSS_PurchaseCompany C ON A.CompanyID = C.CompanyID) A
                                                    WHERE 1=1 AND PhaCode = @PhaCode AND  OrginID = @OrginID";
                return Conn.Query<PHA_Accounts>(query, new { PhaCode = phaCode, OrginID = orginID }).SingleOrDefault();
            }
        }

        public int Update(PHA_Accounts obj)
        {
            using (Conn)
            {
                string query = @"UPDATE PHA_Accounts SET 
                                                            PhaCode = @PhaCode,
                                                            OrginID = @OrginID,
                                                            CompanyID = @CompanyID,
                                                            Stock = @Stock,
                                                            InWarehousePrice = @InWarehousePrice,
                                                            RetailPrice = @RetailPrice,
                                                            WholesalePrice = @WholesalePrice,
                                                            InWarehouseSum = @InWarehouseSum,
                                                            RetailSum = @RetailSum,
                                                            WholesaleSum = @WholesaleSum
                                                      WHERE 
                                                            PhaCode = @PhaCode AND
                                                            OrginID = @OrginID";
                return Conn.Execute(query, obj);
            }
        }
        public int Insert(PHA_Accounts obj)
        {
            using (Conn)
            {
                string query = @"INSERT INTO PHA_Accounts VALUES(
                                                                    @PhaCode,
                                                                    @OrginID,
                                                                    @CompanyID,
                                                                    @Stock,
                                                                    @InWarehousePrice,
                                                                    @RetailPrice,
                                                                    @WholesalePrice,
                                                                    @RetailSum,
                                                                    @WholesaleSum,
                                                                    @InWarehouseSum
                                                                 )";
                return Conn.Execute(query, obj);
            }
        }

        public int Delete(PHA_Accounts obj)
        {
            using (Conn)
            {
                string query = @"DELETE FROM PHA_Accounts WHERE PhaCode=@PhaCode AND OrginID = @OrginID";
                return Conn.Execute(query, obj);
            }
        }


    }
}
