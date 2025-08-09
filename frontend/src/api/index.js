const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

export const createStockIn = async (data) => {
  const response = await fetch(`${API_BASE_URL}/api/stock-ins`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.message || '入库失败')
  }
  
  return response.json()
}

export const getStockIns = async (params = {}) => {
  try {
    // 构建查询参数
    const queryParams = new URLSearchParams();
    if (params.startTime) queryParams.append('startTime', params.startTime);
    if (params.endTime) queryParams.append('endTime', params.endTime);
    
    const queryString = queryParams.toString();
    const url = queryString ? `${API_BASE_URL}/api/stock-ins?${queryString}` : `${API_BASE_URL}/api/stock-ins`;
    
    console.log(`Fetching stock-ins from: ${url}`);
    
    // 添加超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
    
    const response = await fetch(url, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `获取入库记录失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`Received ${data.data?.length || 0} stock-in records`);
    return data;
    
  } catch (error) {
    console.error('Failed to fetch stock-ins:', error);
    if (error.name === 'AbortError') {
      throw new Error('获取入库记录超时，请稍后重试');
    }
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

export const createStockOut = async (data) => {
  const response = await fetch(`${API_BASE_URL}/api/stock-outs`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.message || '出库失败')
  }
  
  return response.json()
}

export const getStockOuts = async (params = {}) => {
  try {
    // 构建查询参数
    const queryParams = new URLSearchParams();
    if (params.startTime) queryParams.append('startTime', params.startTime);
    if (params.endTime) queryParams.append('endTime', params.endTime);
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.pageSize) queryParams.append('pageSize', params.pageSize);
    
    const queryString = queryParams.toString();
    const url = queryString ? `${API_BASE_URL}/api/stock-outs?${queryString}` : `${API_BASE_URL}/api/stock-outs`;
    
    console.log(`Fetching stock-outs from: ${url}`);
    
    // 添加超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
    
    const response = await fetch(url, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `获取出库记录失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`Received ${data.data?.length || 0} stock-out records`);
    return data;
    
  } catch (error) {
    console.error('Failed to fetch stock-outs:', error);
    if (error.name === 'AbortError') {
      throw new Error('获取出库记录超时，请稍后重试');
    }
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

export const updateStockOut = async (id, data) => {
  try {
    console.log(`Updating stock out with ID ${id}:`, data);
    
    const response = await fetch(`${API_BASE_URL}/api/stock-outs/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `更新出库记录失败: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    console.log('Stock out updated successfully:', result);
    return result;
    
  } catch (error) {
    console.error(`Failed to update stock out with ID ${id}:`, error);
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

export const deleteStockOut = async (id) => {
  try {
    console.log(`Deleting stock out with ID ${id}`);
    
    const response = await fetch(`${API_BASE_URL}/api/stock-outs/${id}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `删除出库记录失败: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    console.log('Stock out deleted successfully:', result);
    return result;
    
  } catch (error) {
    console.error(`Failed to delete stock out with ID ${id}:`, error);
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

export const getTodayOutCategoryTotals = async () => {
  try {
    console.log('Fetching today out category totals');
    
    // 添加超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
    
    const response = await fetch(`${API_BASE_URL}/api/stock-outs/category-totals/today`, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `获取今日出库分类总计失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Received today out category totals:', data);
    return data;
    
  } catch (error) {
    console.error('Failed to fetch today out category totals:', error);
    if (error.name === 'AbortError') {
      throw new Error('获取今日出库分类总计超时，请稍后重试');
    }
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

export const getMonthOutCategoryTotals = async () => {
  try {
    console.log('Fetching month out category totals');
    
    // 添加超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
    
    const response = await fetch(`${API_BASE_URL}/api/stock-outs/category-totals/month`, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `获取本月出库分类总计失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Received month out category totals:', data);
    return data;
    
  } catch (error) {
    console.error('Failed to fetch month out category totals:', error);
    if (error.name === 'AbortError') {
      throw new Error('获取本月出库分类总计超时，请稍后重试');
    }
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

export const getTodayCategoryTotals = async () => {
  try {
    console.log('Fetching today category totals');
    
    // 添加超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
    
    const response = await fetch(`${API_BASE_URL}/api/category-totals/today`, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `获取今日分类总计失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Received today category totals:', data);
    return data;
    
  } catch (error) {
    console.error('Failed to fetch today category totals:', error);
    if (error.name === 'AbortError') {
      throw new Error('获取今日分类总计超时，请稍后重试');
    }
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

export const getMonthCategoryTotals = async () => {
  try {
    console.log('Fetching month category totals');
    
    // 添加超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
    
    const response = await fetch(`${API_BASE_URL}/api/category-totals/month`, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `获取本月分类总计失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Received month category totals:', data);
    return data;
    
  } catch (error) {
    console.error('Failed to fetch month category totals:', error);
    if (error.name === 'AbortError') {
      throw new Error('获取本月分类总计超时，请稍后重试');
    }
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

// 获取供应商列表
export const getSuppliers = async (params = {}) => {
  try {
    // 构建查询参数
    const queryParams = new URLSearchParams();
    if (params.search) queryParams.append('search', params.search);
    if (params.page) queryParams.append('page', params.page);
    if (params.pageSize) queryParams.append('pageSize', params.pageSize);
    
    const queryString = queryParams.toString();
    const url = queryString ? `${API_BASE_URL}/api/suppliers?${queryString}` : `${API_BASE_URL}/api/suppliers`;
    
    console.log(`Fetching suppliers from: ${url}`);
    
    // 添加超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
    
    const response = await fetch(url, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `获取供应商列表失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`Received ${data.data?.length || 0} suppliers, total: ${data.total}`);
    return data;
    
  } catch (error) {
    console.error('Failed to fetch suppliers:', error);
    if (error.name === 'AbortError') {
      throw new Error('获取供应商列表超时，请稍后重试');
    }
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

// 获取单个供应商详情
export const getSupplierById = async (id) => {
  try {
    console.log(`Fetching supplier details for ID: ${id}`);
    
    // 添加超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
    
    const response = await fetch(`${API_BASE_URL}/api/suppliers/${id}`, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `获取供应商详情失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Received supplier details:', data);
    return data;
    
  } catch (error) {
    console.error(`Failed to fetch supplier with ID ${id}:`, error);
    if (error.name === 'AbortError') {
      throw new Error('获取供应商详情超时，请稍后重试');
    }
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

// 创建新供应商
export const createSupplier = async (supplierData) => {
  try {
    console.log('Creating new supplier:', supplierData);
    
    const response = await fetch(`${API_BASE_URL}/api/suppliers`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(supplierData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `创建供应商失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Supplier created successfully:', data);
    return data;
    
  } catch (error) {
    console.error('Failed to create supplier:', error);
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

// 更新供应商信息
export const updateSupplier = async (id, supplierData) => {
  try {
    console.log(`Updating supplier with ID ${id}:`, supplierData);
    
    const response = await fetch(`${API_BASE_URL}/api/suppliers/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(supplierData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `更新供应商失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Supplier updated successfully:', data);
    return data;
    
  } catch (error) {
    console.error(`Failed to update supplier with ID ${id}:`, error);
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

// 删除供应商
export const deleteSupplier = async (id) => {
  try {
    console.log(`Deleting supplier with ID ${id}`);
    
    const response = await fetch(`${API_BASE_URL}/api/suppliers/${id}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `删除供应商失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Supplier deleted successfully:', data);
    return data;
    
  } catch (error) {
    console.error(`Failed to delete supplier with ID ${id}:`, error);
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

// 获取每月供应商列表
export const getMonthlySuppliers = async (year, month) => {
  try {
    console.log(`Fetching monthly suppliers for ${year}-${month}`);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
    
    const response = await fetch(
      `${API_BASE_URL}/api/monthly-suppliers?year=${year}&month=${month}`,
      { signal: controller.signal }
    );
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `获取每月供应商失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`Received ${data.data?.length || 0} monthly suppliers`);
    return data;
    
  } catch (error) {
    console.error('Failed to fetch monthly suppliers:', error);
    if (error.name === 'AbortError') {
      throw new Error('获取每月供应商超时，请稍后重试');
    }
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

// 获取所有历史每月供应商记录
export const getAllMonthlySuppliers = async () => {
  try {
    console.log('Fetching all monthly suppliers history');
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
    
    const response = await fetch(
      `${API_BASE_URL}/api/monthly-suppliers/all`,
      { signal: controller.signal }
    );
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `获取历史每月供应商失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`Received ${data.data?.length || 0} monthly supplier records`);
    return data;
    
  } catch (error) {
    console.error('Failed to fetch all monthly suppliers:', error);
    if (error.name === 'AbortError') {
      throw new Error('获取历史每月供应商超时，请稍后重试');
    }
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

// 添加每月供应商
export const addMonthlySupplier = async (supplierId, year, month, supplyItems = []) => {
  try {
    console.log(`Adding monthly supplier: ID ${supplierId} for ${year}-${month} with supply items:`, supplyItems);
    
    const response = await fetch(`${API_BASE_URL}/api/monthly-suppliers`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        supplier_id: supplierId,
        year: parseInt(year),
        month: parseInt(month),
        supply_items: supplyItems
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `添加每月供应商失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Monthly supplier added successfully:', data);
    return data;
    
  } catch (error) {
    console.error('Failed to add monthly supplier:', error);
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}

// 删除每月供应商
export const deleteMonthlySupplier = async (supplierId, year, month) => {
  try {
    console.log(`Deleting monthly supplier: ID ${supplierId} for ${year}-${month}`);
    
    const response = await fetch(
      `${API_BASE_URL}/api/monthly-suppliers/${supplierId}?year=${year}&month=${month}`,
      { method: 'DELETE' }
    );
    
    if (!response.ok) {
      const error = await response.json();
      console.error('API error:', error);
      throw new Error(error.message || `删除每月供应商失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Monthly supplier deleted successfully:', data);
    return data;
    
  } catch (error) {
    console.error('Failed to delete monthly supplier:', error);
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('网络连接失败，请检查网络连接');
    }
    throw error;
  }
}