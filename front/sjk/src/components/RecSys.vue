<template>
  <div>
    <el-header>
      <div style="text-align: center;">
        <h1>推荐系统</h1>
      </div>
    </el-header>
    <el-main>

      <el-table :data="tableData" style="width: 100%">
        <el-table-column prop="Name" label="被保险人" width="420" align="center"></el-table-column>
        <el-table-column prop="Insurer" label="保险公司" width="420" align="center"></el-table-column>
        <el-table-column prop="ProductName" label="保险名称" width="420" align="center"></el-table-column>
        <el-table-column prop="Type" label="保险类型" width="420" align="center"></el-table-column>
        <el-table-column prop="Term" label="保障期限" width="420" align="center"></el-table-column>
      </el-table>

    </el-main>
  </div>
</template>

<script>
export default {
  created() {
    this.getdata();
  },
  data() {
    return {
      tableData: [],
    }
  },
  methods: {
    getdata() {
      this.$axios.get("/api/recommended").then((res) => {
        console.log(res.data);
        if (res.data.status == 200) {
          this.tableData = res.data.tabledata;
        }
      })
    },

  }
}
</script>

<style scoped>

</style>