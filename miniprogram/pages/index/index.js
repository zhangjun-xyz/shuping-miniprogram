//index.js
const app = getApp()

Page({
  data: {
    imageUrl: '',
    isLoading: false,
    loadingText: '处理中...',
    showManualForm: false,
    bookTitle: '',
    bookAuthor: '',
    bookPublisher: ''
  },

  onLoad: function() {
    console.log('首页加载完成')
  },

  // 拍照
  takePhoto: function() {
    const that = this
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera'],
      camera: 'back',
      success: function(res) {
        const imageUrl = res.tempFiles[0].tempFilePath
        that.setData({
          imageUrl: imageUrl
        })
      },
      fail: function(error) {
        console.error('拍照失败:', error)
        wx.showToast({
          title: '拍照失败，请重试',
          icon: 'none'
        })
      }
    })
  },

  // 从相册选择
  chooseImage: function() {
    const that = this
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album'],
      success: function(res) {
        const imageUrl = res.tempFiles[0].tempFilePath
        that.setData({
          imageUrl: imageUrl
        })
      },
      fail: function(error) {
        console.error('选择图片失败:', error)
        wx.showToast({
          title: '选择图片失败，请重试',
          icon: 'none'
        })
      }
    })
  },

  // 清除图片
  clearImage: function() {
    this.setData({
      imageUrl: ''
    })
  },

  // 测试网络连接
  testConnection: function() {
    const app = getApp()
    const apiUrl = app.globalData.apiBaseUrl
    console.log('=== 开始测试连接 ===')
    console.log('API地址:', apiUrl)
    console.log('完整请求URL:', `${apiUrl}/health`)

    wx.request({
      url: `${apiUrl}/health`,
      method: 'GET',
      timeout: 10000,
      success: function(res) {
        console.log('=== 连接成功 ===')
        console.log('响应状态:', res.statusCode)
        console.log('响应数据:', res.data)
        wx.showToast({
          title: '网络连接正常',
          icon: 'success'
        })
      },
      fail: function(error) {
        console.log('=== 连接失败 ===')
        console.error('错误详情:', error)
        console.error('错误代码:', error.errMsg)
        wx.showToast({
          title: `连接失败: ${error.errMsg}`,
          icon: 'none',
          duration: 3000
        })
      }
    })
  },

  // 识别书籍
  recognizeBook: function() {
    if (!this.data.imageUrl) {
      wx.showToast({
        title: '请先选择图片',
        icon: 'none'
      })
      return
    }

    this.setData({
      isLoading: true,
      loadingText: '正在识别书籍...'
    })

    // 上传图片到服务器
    this.uploadImageAndRecognize()
  },

  // 上传图片并识别
  uploadImageAndRecognize: function() {
    const that = this

    wx.uploadFile({
      url: `${app.globalData.apiBaseUrl}/api/recognize-book`,
      filePath: that.data.imageUrl,
      name: 'image',
      header: {
        'content-type': 'multipart/form-data'
      },
      success: function(res) {
        try {
          const data = JSON.parse(res.data)
          that.handleRecognitionResult(data)
        } catch (error) {
          console.error('解析响应失败:', error)
          that.showError('服务器响应格式错误')
        }
      },
      fail: function(error) {
        console.error('上传失败:', error)
        that.showError('上传失败，请检查网络连接')
      },
      complete: function() {
        that.setData({
          isLoading: false
        })
      }
    })
  },

  // 处理识别结果
  handleRecognitionResult: function(data) {
    if (data.success) {
      // 跳转到结果页面
      wx.navigateTo({
        url: `/pages/result/result?data=${encodeURIComponent(JSON.stringify(data.data))}`
      })
    } else {
      this.showError(data.error || '识别失败')
    }
  },

  // 显示手动输入表单
  manualInput: function() {
    this.setData({
      showManualForm: true,
      imageUrl: '' // 清除图片
    })
  },

  // 取消手动输入
  cancelManualInput: function() {
    this.setData({
      showManualForm: false,
      bookTitle: '',
      bookAuthor: '',
      bookPublisher: ''
    })
  },

  // 输入事件
  onTitleInput: function(e) {
    this.setData({
      bookTitle: e.detail.value
    })
  },

  onAuthorInput: function(e) {
    this.setData({
      bookAuthor: e.detail.value
    })
  },

  onPublisherInput: function(e) {
    this.setData({
      bookPublisher: e.detail.value
    })
  },

  // 手动输入搜索
  searchByManualInput: function() {
    if (!this.data.bookTitle.trim()) {
      wx.showToast({
        title: '请输入书名',
        icon: 'none'
      })
      return
    }

    this.setData({
      isLoading: true,
      loadingText: '正在搜索...'
    })

    const that = this
    app.request({
      url: '/api/search-douban',
      method: 'POST',
      data: {
        title: this.data.bookTitle.trim(),
        author: this.data.bookAuthor.trim() || undefined,
        publisher: this.data.bookPublisher.trim() || undefined
      }
    }).then(function(data) {
      if (data.success) {
        // 构造结果数据
        const resultData = {
          book_info: {
            title: that.data.bookTitle.trim(),
            author: that.data.bookAuthor.trim(),
            publisher: that.data.bookPublisher.trim()
          },
          douban_info: data.data,
          use_ai: false
        }

        // 跳转到结果页面
        wx.navigateTo({
          url: `/pages/result/result?data=${encodeURIComponent(JSON.stringify(resultData))}`
        })
      } else {
        that.showError(data.error || '搜索失败')
      }
    }).catch(function(error) {
      console.error('搜索失败:', error)
      that.showError('搜索失败，请检查网络连接')
    }).finally(function() {
      that.setData({
        isLoading: false
      })
    })
  },

  // 显示错误信息
  showError: function(message) {
    wx.showModal({
      title: '提示',
      content: message,
      showCancel: false,
      confirmText: '知道了'
    })
  }
})