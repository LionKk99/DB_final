<template>
    <div>
      <el-header>
        <div style="text-align: center;">
          <h1>家庭保单</h1>
        </div>
      </el-header>

      <el-main>

        <el-row :gutter="20" class = 'bd_row'>

          <!-- 添加保单 -->
          <el-button type="primary"  @click="showadd()">添加保单</el-button>
          &nbsp;
          &nbsp;
          &nbsp;
          &nbsp;
          &nbsp;
          &nbsp;
          <!-- 下拉菜单 -->
          <el-dropdown @command="handleCommand">
                    <span class="el-dropdown-link">
                      被保险人<i class="el-icon-arrow-down el-icon--right"></i>
                    </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item v-for="Name in names" :key="Name" :command="Name">{{ Name }}</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </el-row>


        <el-table :data="tableData" style="width: 100%">
          <el-table-column prop="PolicyID" label="保单号" width="210" align="center"></el-table-column>
          <el-table-column prop="Name" label="被保险人" width="210" align="center"></el-table-column>
          <el-table-column prop="Insurer" label="保险公司" width="210" align="center"></el-table-column>
          <el-table-column prop="Type" label="保险类型" width="210" align="center"></el-table-column>
          <el-table-column prop="CoverageAmount" label="保额" width="210" align="center"></el-table-column>
          <el-table-column prop="ProductName" label="保险名称" width="210" align="center"></el-table-column>
          <el-table-column prop="PaymentAmount" label="下次缴费金额" width="210" align="center"></el-table-column>
          <el-table-column prop="NextPaymentData" label="下次缴费日期" width="210" align="center"></el-table-column>
          <el-table-column prop="status" label="状态" width="210" align="center"></el-table-column>
          <el-table-column prop="operate" label="操作" width="400" align="center">
            <template slot-scope="scope">
              <el-button type="success" @click="detail(scope.row)">查询</el-button>
              <el-button type="primary" @click="remake(scope.row)">修改</el-button>
              <el-button type="danger" @click="del(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-dialog title="添加保单" :visible.sync="dialog_add" width="40%" center>
          <div>
            <el-form ref="form" :model="form_add" label-width="100px">
              <el-form-item label="身份证号：">
                <el-input v-model="form_add.IDNumber"></el-input>
              </el-form-item>
              <el-form-item label="保险公司：">
                <el-input v-model="form_add.Insurer"></el-input>
              </el-form-item>
              <el-form-item label="保险名称：">
                <el-input v-model="form_add.ProductName"></el-input>
              </el-form-item>
              <el-form-item label="保单号：">
                <el-input v-model="form_add.PolicyID"></el-input>
              </el-form-item>
              <el-form-item label="保险生效日：">
                <el-input v-model="form_add.EffectiveDate"></el-input>
              </el-form-item>
              <el-form-item label="首次缴费日：">
                <el-input v-model="form_add.FirstPaymentDate"></el-input>
              </el-form-item>
              <el-form-item label="银行卡尾号：">
                <el-input v-model="form_add.CardLastDigits"></el-input>
              </el-form-item>
              <el-form-item label="投保人：">
                <el-input v-model="form_add.Policyholder"></el-input>
              </el-form-item>

            </el-form>

            <div style="text-align: center;">
              <el-button type="primary" @click="add()">
                提交
              </el-button>
            </div>

          </div>
        </el-dialog>

        <el-dialog title="详细信息" :visible.sync="dialog_det" width="30%" center>
            <div ref="contentToExport">
              <div style="text-align: center;font-size: 22px;">
                {{Insurer}}&nbsp;&nbsp;{{ ProductName }}
              </div>
              <br>
              <div style="font-size: 20px;">
                {{Type}}
              </div>
              <br>

              <div>
                <el-descriptions class="margin-top" title="个人信息" :model="form_det" column="2" >
                  <el-descriptions-item label="被保险人">{{ form_det.Name }}</el-descriptions-item>
                  <el-descriptions-item label="身份证">{{ form_det.IDNumber }}</el-descriptions-item>
                  <el-descriptions-item label="缴费尾号">{{ form_det.BankAccountLastDigits }}</el-descriptions-item>
                  <el-descriptions-item label="投保人">{{ form_det.Policyholder}}</el-descriptions-item>
                </el-descriptions>
                <br>

                <el-descriptions class="margin-top" title="保单概况" :model="form_det" column="2" >
                  <el-descriptions-item label="保单号">{{ form_det.PolicyID}}</el-descriptions-item>
                  <el-descriptions-item label="保险生效日">{{ form_det.EffectiveDate}}</el-descriptions-item>
                  <el-descriptions-item label="保险状态">{{ form_det.status}}</el-descriptions-item>
                  <el-descriptions-item label="单次缴费金额">{{ form_det.PaymentAmount }}</el-descriptions-item>
                  <el-descriptions-item label="单次缴费频率">{{ form_det.PaymentFrequency }}</el-descriptions-item>
                  <el-descriptions-item label="缴费时长">{{ form_det.Totalpaymenttime }}</el-descriptions-item>
                  <el-descriptions-item label="保障期限">{{ form_det.Term }}</el-descriptions-item>
                  <el-descriptions-item label="保额">{{ form_det.CoverageAmount }}</el-descriptions-item>
                </el-descriptions>
                <br>

                <el-descriptions class="margin-top" title="理赔记录" :column="2" v-for="(claim, index) in claims" :key="index">
                  <el-descriptions-item label="理赔单号">{{ claim.ClaimNumber }}</el-descriptions-item>
                  <el-descriptions-item label="理赔金额">{{ claim.ClaimAmount }}</el-descriptions-item>
                  <el-descriptions-item label="理赔时间">{{ claim.ClaimTime }}</el-descriptions-item>
                  <el-descriptions-item label="理赔原因">{{ claim.Reason }}</el-descriptions-item>
                </el-descriptions>
              </div>
            </div>


            <br>

            <div style="text-align: center;">
              <el-button type="primary" @click="exportToPDF()">
                导出
              </el-button>
              <el-button type="primary" @click="importPDF()">
                导入pdf
              </el-button>
              <el-button type="primary" @click="exportpdf()">
                导出pdf
              </el-button>
            </div>

        </el-dialog>

        <el-dialog title="修改保单" :visible.sync="dialog_re" width="40%" center>
          <div>
            <el-form ref="form" :model="form_re" label-width="100px">
              <el-form-item label="身份证号：">
                <el-input v-model="form_re.IDNumber"></el-input>
              </el-form-item>
              <el-form-item label="保险公司：">
                <el-input v-model="form_re.Insurer"></el-input>
              </el-form-item>
              <el-form-item label="保险名称：">
                <el-input v-model="form_re.ProductName"></el-input>
              </el-form-item>
              <el-form-item label="保单号：">
                <el-input v-model="form_re.PolicyID"></el-input>
              </el-form-item>
              <el-form-item label="保险生效日：">
                <el-input v-model="form_re.EffectiveDate"></el-input>
              </el-form-item>
              <el-form-item label="首次缴费日：">
                <el-input v-model="form_re.FirstPaymentDate"></el-input>
              </el-form-item>
              <el-form-item label="银行卡尾号：">
                <el-input v-model="form_re.CardLastDigits"></el-input>
              </el-form-item>
              <el-form-item label="投保人：">
                <el-input v-model="form_re.Policyholder"></el-input>
              </el-form-item>
            </el-form>
            <div style="text-align: center;">
              <el-button type="primary" @click="change()">
                确认修改
              </el-button>
            </div>
          </div>
        </el-dialog>

        <el-dialog title="提醒" :visible.sync="dialog_recent" width="40%" center>
          <div>
            <el-table :data="recent" style="width: 100%">
            <el-table-column prop="PolicyID" label="保单号" width="210" align="center"></el-table-column>
            <el-table-column prop="Name" label="被保险人" width="210" align="center"></el-table-column>
            <el-table-column prop="Insurer" label="保险公司" width="210" align="center"></el-table-column>
            <el-table-column prop="Type" label="保险类型" width="210" align="center"></el-table-column>
            <el-table-column prop="CoverageAmount" label="保额" width="210" align="center"></el-table-column>
            <el-table-column prop="ProductName" label="保险名称" width="210" align="center"></el-table-column>
            <el-table-column prop="PaymentAmount" label="下次缴费金额" width="210" align="center"></el-table-column>
            <el-table-column prop="NextPaymentData" label="下次缴费日期" width="210" align="center"></el-table-column>
            <el-table-column prop="status" label="状态" width="210" align="center"></el-table-column>
          </el-table>
          </div>
        </el-dialog>
        <el-dialog  :visible.sync="dialog_pdf" width="40%" center>
          <div>
            <el-form ref="form" :model="form_pdf" label-width="100px">
              <el-form-item label="导入地址：">
                <el-input v-model="form_pdf.path"></el-input>
              </el-form-item>
            </el-form>
            <div style="text-align: center;">
              <el-button type="primary" @click="pdf()">
                确认导入
              </el-button>
            </div>
          </div>
        </el-dialog>

      </el-main>
    </div>
</template>

<script>
import html2pdf from 'html2pdf.js';
export default {
    created() {
      this.getdata();
      this.getname();
      this.getrecent();
    },
    data() {
      return {
        originalData:[],
        tableData: [],
        dialog_add: false,
        form_add:{
          IDNumber:'',
          Insurer:'',
          ProductName:'',
          PolicyID:'',
          EffectiveDate:'',
          FirstPaymentDate:'',
          CardLastDigits:'',
          Policyholder:'',
        },
        names:[],
        dialog_det: false,
        form_det:{
          Insurer:'',
          ProductName:'',
          Type:'',
          Name:'',
          IDNumber:'',
          BankAccountLastDigits:'',
          PolicyID:'',
          EffectiveDate:'',
          status:'',
          PaymentAmount:'',
          PaymentFrequency:'',
          Totalpaymenttime:'',
          Term:'',
          CoverageAmount:'',
          Policyholder:'',
        },
        dialog_re: false,
        form_re:{
          IDNumber:'',
          Insurer:'',
          ProductName:'',
          PolicyID:'',
          EffectiveDate:'',
          FirstPaymentDate:'',
          CardLastDigits:'',
          old:'',
          Policyholder:'',
        },
        dialog_recent: true,
        recent:[],
        Insurer:'',
        ProductName:'',
        Type:'',
        claims: [],
        dialog_pdf: false,
        form_pdf:{path:'',policy_id:''}
      }
    },
    methods: {
      getrecent(){
        this.$axios.get("/api/recentpolicy").then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.recent = res.data.tabledata;
          }
        })
      },
      getdata() {
        this.$axios.get("/api/insurance").then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.originalData = res.data.tabledata;
            this.tableData = this.originalData
          }
        })
      },
      showadd(){
        this.dialog_add=true
      },
      add(){
        this.$axios.post("/api/addpolicy", this.form_add).then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.$message({
              message: "成功添加",
              type: "success"
            })
            this.dialog_add = false;
            this.getdata();
          }
        })
      },
      getname() {
        this.$axios.get("/api/insurance").then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.names = [...new Set(res.data.tabledata.map(item => item.Name))];
            this.names.push("全部")
          }
        })
      },
      handleCommand(command) {
        if (command === "全部") {
          this.tableData = this.originalData;
        } else {
          this.tableData = this.originalData.filter(item => item.Name === command);
        }
      },
      detail(row){
        this.dialog_det=true;
        this.policy_id = row.PolicyID;
        this.$axios.get("/api/overview",{ params: { policy_id: this.policy_id } }).then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.form_det.Insurer = res.data.policyDetail.Insurer
            this.form_det.ProductName = res.data.policyDetail.ProductName
            this.form_det.Type = res.data.policyDetail.Type
            this.form_det.Name = res.data.policyDetail.Name
            this.form_det.IDNumber = res.data.policyDetail.IDNumber
            this.form_det.BankAccountLastDigits = res.data.policyDetail.BankAccountLastDigits
            this.form_det.PolicyID = res.data.policyDetail.PolicyID
            this.form_det.EffectiveDate = res.data.policyDetail.EffectiveDate
            this.form_det.status = res.data.policyDetail.status
            this.form_det.PaymentAmount = res.data.policyDetail.PaymentAmount
            this.form_det.PaymentFrequency = res.data.policyDetail.PaymentFrequency
            this.form_det.Totalpaymenttime = res.data.policyDetail.Totalpaymenttime
            this.form_det.Term = res.data.policyDetail.Term
            this.form_det.CoverageAmount = res.data.policyDetail.CoverageAmount
            this.form_det.Policyholder = res.data.policyDetail.Policyholder}
            this.Insurer = res.data.policyDetail.Insurer
            this.ProductName = res.data.policyDetail.ProductName
            this.Type = res.data.policyDetail.Type
            this.claims = res.data.claimsRecords
        })
      },
      del(row){
        this.delete_id = row.PolicyID;
        this.$axios.delete("/api/insurance", { data: { delete_id: this.delete_id } }).then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.$message({
              message: res.data.msg,
              type: "success"
            })
            this.getdata()
          }
        })
      },
      remake(row){
        this.dialog_re=true;
        this.policy_id = row.PolicyID;
        this.$axios.get("/api/getpolicy",{ params: { policy_id: this.policy_id } }).then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.form_re.IDNumber = res.data.tabledata.IDNumber
            this.form_re.Insurer = res.data.tabledata.Insurer
            this.form_re.ProductName = res.data.tabledata.ProductName
            this.form_re.PolicyID = res.data.tabledata.PolicyID
            this.form_re.EffectiveDate = res.data.tabledata.EffectiveDate
            this.form_re.FirstPaymentDate = res.data.tabledata.FirstPaymentdata
            this.form_re.CardLastDigits = res.data.tabledata.BankAccountLastDigits
            this.form_re.old  = res.data.tabledata.PolicyID
            this.form_re.Policyholder  = res.data.tabledata.Policyholder
            }
        })
      },
      change(){
        this.$axios.post("/api/updatepolicy", this.form_re).then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.$message({
              message: "成功修改",
              type: "success"
            })
            this.dialog_re = false;
            this.getdata();
          }
        })
      },
      exportToPDF() {
        // 获取需要导出的区域，这里假设使用 ref 获取
        const contentToExport = this.$refs.contentToExport;

        // 设置 PDF 导出的选项，可以根据需要调整
        const options = {
          margin: 1,
          filename: '详细信息.pdf',
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 2 },
          jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
        };

        // 使用 html2pdf 将内容导出为 PDF 并自动下载
        html2pdf().from(contentToExport).set(options).save();
      },
      importPDF(){
        this.dialog_pdf=true;
      },
      pdf(){
        this.form_pdf.policy_id = this.form_det.PolicyID;
        this.$axios.post("/api/pdf", this.form_pdf).then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.$message({
              message: "成功",
              type: "success"
            })
            this.dialog_pdf = false;
            this.getdata();
          }
        })
      },
      exportpdf() {
        this.policy_id = this.form_det.PolicyID;
        console.log(`Sending policy_id: ${this.policy_id}`);  // 打印发送的参数
        this.$axios.get("/api/downloadpdf", { params: { policy_id: this.policy_id }, responseType: 'blob' })
            .then(response => {
              // 检查是否是 JSON 响应（错误信息）
              const contentType = response.headers['content-type'];
              if (contentType && contentType.indexOf('application/json') !== -1) {
                const reader = new FileReader();
                reader.onload = () => {
                  const errorResponse = JSON.parse(reader.result);
                  this.$message({
                    message: errorResponse.msg,
                    type: "error"
                  });
                };
                reader.readAsText(response.data);
                return;
              }

              // 如果是 PDF 响应，则触发下载
              const blob = new Blob([response.data], { type: 'application/pdf' });
              const link = document.createElement('a');
              link.href = window.URL.createObjectURL(blob);
              link.download = `${this.policy_id}.pdf`;
              link.click();
              this.$message({
                message: "PDF 文件下载成功",
                type: "success"
              });
            })
            .catch(error => {
              console.error('Error downloading PDF:', error);
              this.$message({
                message: '下载 PDF 文件失败',
                type: 'error'
              });
            });
      }
    }
}
</script>

<style scoped>

</style>