//app.js
App({
  globalData: {
    // API服务器地址 - 本地开发环境
    apiBaseUrl: 'http://localhost:5002',
    userInfo: null
  },

  onLaunch: function () {
    console.log('书评助手小程序启动')

    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    // 获取用户信息
    this.getUserProfile()
  },

  getUserProfile: function() {
    if (wx.getUserProfile) {
      // 支持新版getUserProfile API
      this.globalData.supportNewAPI = true
    }
  },

  // 全局方法：显示加载提示
  showLoading: function(title = '加载中...') {
    wx.showLoading({
      title: title,
      mask: true
    })
  },

  // 全局方法：隐藏加载提示
  hideLoading: function() {
    wx.hideLoading()
  },

  // 全局方法：显示提示消息
  showToast: function(title, icon = 'none') {
    wx.showToast({
      title: title,
      icon: icon,
      duration: 2000
    })
  },

  // 全局方法：API请求
  request: function(options) {
    const app = this

    return new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.apiBaseUrl}${options.url}`,
        method: options.method || 'GET',
        data: options.data || {},
        header: {
          'content-type': 'application/json',
          ...options.header
        },
        success: function(res) {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else {
            reject(new Error(`请求失败: ${res.statusCode}`))
          }
        },
        fail: function(error) {
          reject(error)
        }
      })
    })
  }
})