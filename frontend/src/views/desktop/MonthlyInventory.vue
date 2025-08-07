<template>
  <div class="monthly-inventory">
    <div class="page-header">
      <h2>月底盘点明细</h2>
    </div>

    <!-- 月底库存卡片 -->
    <div class="card">
      <div class="card-header">
        <h3>月底库存</h3>
        <button class="btn btn-primary" @click="showAddInventoryDialog = true">
          添加库存记录
        </button>
      </div>
      <div class="card-body">
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>时间（年月）</th>
                <th>名称</th>
                <th>单价（元）</th>
                <th>库存数量</th>
                <th>库存金额（元）</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in inventoryList" :key="index">
                <td>{{ item.date }}</td>
                <td>{{ item.name }}</td>
                <td>{{ item.unitPrice.toFixed(2) }}</td>
                <td>{{ item.quantity }}</td>
                <td>{{ (item.unitPrice * item.quantity).toFixed(2) }}</td>
                <td>
                  <button class="btn btn-sm btn-danger" @click="deleteInventoryItem(index)">
                    删除
                  </button>
                </td>
              </tr>
              <tr v-if="inventoryList.length === 0">
                <td colspan="6" class="text-center">暂无数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 出库分类卡片 -->
    <div class="card">
      <div class="card-header">
        <h3>出库分类</h3>
        <button class="btn btn-primary" @click="showAddCategoryDialog = true">
          添加分类
        </button>
      </div>
      <div class="card-body">
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>分类名称</th>
                <th>单位</th>
                <th>单价（元）</th>
                <th>规格</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(category, index) in categoryList" :key="index">
                <td>{{ category.name }}</td>
                <td>{{ category.unit }}</td>
                <td>{{ category.unitPrice.toFixed(2) }}</td>
                <td>{{ category.specification }}</td>
                <td>
                  <button class="btn btn-sm btn-warning" @click="editCategory(index)">
                    编辑
                  </button>
                  <button class="btn btn-sm btn-danger" @click="deleteCategory(index)">
                    删除
                  </button>
                </td>
              </tr>
              <tr v-if="categoryList.length === 0">
                <td colspan="5" class="text-center">暂无数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 添加库存记录对话框 -->
    <div v-if="showAddInventoryDialog" class="modal-overlay" @click="closeAddInventoryDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h4>添加库存记录</h4>
          <button class="close-btn" @click="closeAddInventoryDialog">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addInventoryItem">
            <div class="form-group">
              <label>时间（年月）：</label>
              <input 
                type="month" 
                v-model="newInventoryItem.date" 
                class="form-control" 
                required
              >
            </div>
            <div class="form-group">
              <label>名称：</label>
              <select v-model="newInventoryItem.name" class="form-control" required>
                <option value="">请选择分类</option>
                <option v-for="category in categoryList" :key="category.name" :value="category.name">
                  {{ category.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>单价（元）：</label>
              <input 
                type="number" 
                step="0.01" 
                v-model.number="newInventoryItem.unitPrice" 
                class="form-control" 
                required
                :readonly="selectedCategoryPrice !== null"
              >
            </div>
            <div class="form-group">
              <label>库存数量：</label>
              <input 
                type="number" 
                step="0.01" 
                v-model.number="newInventoryItem.quantity" 
                class="form-control" 
                required
              >
            </div>
            <div class="form-group">
              <label>库存金额（元）：</label>
              <input 
                type="text" 
                :value="(newInventoryItem.unitPrice * newInventoryItem.quantity || 0).toFixed(2)" 
                class="form-control" 
                readonly
              >
            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn-primary">确认添加</button>
              <button type="button" class="btn btn-secondary" @click="closeAddInventoryDialog">取消</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 添加/编辑分类对话框 -->
    <div v-if="showAddCategoryDialog" class="modal-overlay" @click="closeAddCategoryDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h4>{{ editingCategoryIndex !== -1 ? '编辑分类' : '添加分类' }}</h4>
          <button class="close-btn" @click="closeAddCategoryDialog">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addOrUpdateCategory">
            <div class="form-group">
              <label>分类名称：</label>
              <input 
                type="text" 
                v-model="newCategory.name" 
                class="form-control" 
                required
              >
            </div>
            <div class="form-group">
              <label>单位：</label>
              <select v-model="newCategory.unit" class="form-control" required>
                <option value="千克">千克</option>
                <option value="升">升</option>
              </select>
            </div>
            <div class="form-group">
              <label>单价（元）：</label>
              <input 
                type="number" 
                step="0.01" 
                v-model.number="newCategory.unitPrice" 
                class="form-control" 
                required
              >
            </div>
            <div class="form-group">
              <label>规格：</label>
              <input 
                type="text" 
                v-model="newCategory.specification" 
                class="form-control" 
                placeholder="选填"
              >
            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn-primary">
                {{ editingCategoryIndex !== -1 ? '确认修改' : '确认添加' }}
              </button>
              <button type="button" class="btn btn-secondary" @click="closeAddCategoryDialog">取消</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MonthlyInventory',
  data() {
    return {
      // 库存列表
      inventoryList: [],
      // 分类列表
      categoryList: [],
      // 对话框显示状态
      showAddInventoryDialog: false,
      showAddCategoryDialog: false,
      // 新库存记录
      newInventoryItem: {
        date: '',
        name: '',
        unitPrice: 0,
        quantity: 0
      },
      // 新分类
      newCategory: {
        name: '',
        unit: '千克',
        unitPrice: 0,
        specification: ''
      },
      // 编辑状态
      editingCategoryIndex: -1
    }
  },
  computed: {
    selectedCategoryPrice() {
      const selectedCategory = this.categoryList.find(cat => cat.name === this.newInventoryItem.name);
      return selectedCategory ? selectedCategory.unitPrice : null;
    }
  },
  watch: {
    'newInventoryItem.name'(newName) {
      const selectedCategory = this.categoryList.find(cat => cat.name === newName);
      if (selectedCategory) {
        this.newInventoryItem.unitPrice = selectedCategory.unitPrice;
      }
    }
  },
  mounted() {
    this.loadData();
  },
  methods: {
    // 加载数据
    loadData() {
      // 从localStorage加载数据
      const savedInventory = localStorage.getItem('monthlyInventory');
      const savedCategories = localStorage.getItem('outboundCategories');
      
      if (savedInventory) {
        this.inventoryList = JSON.parse(savedInventory);
      }
      
      if (savedCategories) {
        this.categoryList = JSON.parse(savedCategories);
      }
    },
    
    // 保存数据到localStorage
    saveData() {
      localStorage.setItem('monthlyInventory', JSON.stringify(this.inventoryList));
      localStorage.setItem('outboundCategories', JSON.stringify(this.categoryList));
    },
    
    // 添加库存记录
    addInventoryItem() {
      this.inventoryList.push({
        date: this.newInventoryItem.date,
        name: this.newInventoryItem.name,
        unitPrice: this.newInventoryItem.unitPrice,
        quantity: this.newInventoryItem.quantity
      });
      
      this.saveData();
      this.closeAddInventoryDialog();
    },
    
    // 删除库存记录
    deleteInventoryItem(index) {
      if (confirm('确定要删除这条库存记录吗？')) {
        this.inventoryList.splice(index, 1);
        this.saveData();
      }
    },
    
    // 添加或更新分类
    addOrUpdateCategory() {
      if (this.editingCategoryIndex !== -1) {
        // 编辑模式
        this.categoryList[this.editingCategoryIndex] = { ...this.newCategory };
      } else {
        // 添加模式
        this.categoryList.push({ ...this.newCategory });
      }
      
      this.saveData();
      this.closeAddCategoryDialog();
    },
    
    // 编辑分类
    editCategory(index) {
      this.editingCategoryIndex = index;
      this.newCategory = { ...this.categoryList[index] };
      this.showAddCategoryDialog = true;
    },
    
    // 删除分类
    deleteCategory(index) {
      if (confirm('确定要删除这个分类吗？')) {
        this.categoryList.splice(index, 1);
        this.saveData();
      }
    },
    
    // 关闭添加库存对话框
    closeAddInventoryDialog() {
      this.showAddInventoryDialog = false;
      this.newInventoryItem = {
        date: '',
        name: '',
        unitPrice: 0,
        quantity: 0
      };
    },
    
    // 关闭添加分类对话框
    closeAddCategoryDialog() {
      this.showAddCategoryDialog = false;
      this.editingCategoryIndex = -1;
      this.newCategory = {
        name: '',
        unit: '千克',
        unitPrice: 0,
        specification: ''
      };
    }
  }
}
</script>

<style scoped>
.monthly-inventory {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.card-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.card-body {
  padding: 20px;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.data-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.data-table tbody tr:hover {
  background: #f8f9fa;
}

.text-center {
  text-align: center;
  color: #6c757d;
  font-style: italic;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
}

.btn-warning:hover {
  background: #e0a800;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
  margin-right: 5px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h4 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6c757d;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.form-control[readonly] {
  background-color: #e9ecef;
  opacity: 1;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 30px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .monthly-inventory {
    padding: 10px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .data-table {
    font-size: 12px;
  }
  
  .data-table th,
  .data-table td {
    padding: 8px;
  }
  
  .modal-content {
    width: 95%;
    margin: 10px;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>