//index.js
const app = getApp()

Page({
  data: {
    isLoading: false,
    loadingText: '处理中...'
  },

  onLoad: function() {
    console.log('首页加载完成')
  },

  onShow: function() {
    // 页面显示时，重置loading状态（处理从结果页返回的情况）
    this.setData({
      isLoading: false
    })
  },

  // 拍照并自动识别
  takePhotoAndRecognize: function() {
    const that = this
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera'],
      camera: 'back',
      success: function(res) {
        const imageUrl = res.tempFiles[0].tempFilePath
        // 拍照成功后立即识别
        that.recognizeBookImage(imageUrl)
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

  // 从相册选择并自动识别
  chooseImageAndRecognize: function() {
    const that = this
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album'],
      success: function(res) {
        const imageUrl = res.tempFiles[0].tempFilePath
        // 选择成功后立即识别
        that.recognizeBookImage(imageUrl)
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

  // 识别书籍图片
  recognizeBookImage: function(imageUrl) {
    if (!imageUrl) {
      wx.showToast({
        title: '图片无效，请重试',
        icon: 'none'
      })
      return
    }

    this.setData({
      isLoading: true,
      loadingText: '正在压缩图片...'
    })

    // 上传图片到服务器并识别
    this.uploadImageAndRecognize(imageUrl)
  },

  // 上传图片并识别
  uploadImageAndRecognize: function(imageUrl) {
    const that = this

    // 先获取图片信息，根据大小和尺寸动态决定压缩策略
    wx.getFileInfo({
      filePath: imageUrl,
      success: function(fileInfo) {
        const fileSizeMB = fileInfo.size / 1024 / 1024
        console.log(`原图大小: ${fileSizeMB.toFixed(2)}MB`)

        // 获取图片尺寸
        wx.getImageInfo({
          src: imageUrl,
          success: function(imageInfo) {
            const width = imageInfo.width
            const height = imageInfo.height
            console.log(`原图尺寸: ${width}×${height}`)

            // 动态决定压缩策略
            const compressConfig = that.getCompressConfig(fileSizeMB, width, height)

            if (compressConfig.needCompress) {
              console.log(`压缩策略: 质量${compressConfig.quality}, 宽度${compressConfig.width}`)
              that.compressAndUpload(imageUrl, compressConfig, fileSizeMB)
            } else {
              console.log('图片已足够小，跳过压缩直接上传')
              that.setData({
                loadingText: '正在上传图片...'
              })
              that.doUpload(imageUrl)
            }
          },
          fail: function(err) {
            console.warn('获取图片尺寸失败，使用默认压缩策略:', err)
            // 如果获取尺寸失败，使用默认中度压缩
            that.compressAndUpload(imageUrl, { quality: 85, width: 1920 }, fileSizeMB)
          }
        })
      },
      fail: function(err) {
        console.warn('获取文件信息失败，使用原图:', err)
        that.setData({
          loadingText: '正在上传图片...'
        })
        that.doUpload(imageUrl)
      }
    })
  },

  // 根据图片大小和尺寸获取压缩配置
  getCompressConfig: function(fileSizeMB, width, height) {
    // 小于300KB且尺寸不大，不需要压缩
    if (fileSizeMB < 0.3 && width <= 1920 && height <= 1920) {
      return { needCompress: false }
    }

    // 小于800KB但尺寸较大，轻度压缩保留高质量
    if (fileSizeMB < 0.8 && width <= 2400) {
      return {
        needCompress: true,
        quality: 90,
        width: 2048
      }
    }

    // 小于2MB，轻度压缩
    if (fileSizeMB < 2) {
      return {
        needCompress: true,
        quality: 88,
        width: 1920
      }
    }

    // 2MB-5MB，中度压缩
    if (fileSizeMB < 5) {
      return {
        needCompress: true,
        quality: 85,
        width: 1920
      }
    }

    // 5MB-10MB，较强压缩
    if (fileSizeMB < 10) {
      return {
        needCompress: true,
        quality: 80,
        width: 1600
      }
    }

    // 超过10MB，强力压缩
    return {
      needCompress: true,
      quality: 75,
      width: 1440
    }
  },

  // 执行压缩并上传
  compressAndUpload: function(imageUrl, config, originalSizeMB) {
    const that = this
    const compressStartTime = Date.now()

    wx.compressImage({
      src: imageUrl,
      quality: config.quality,
      compressedWidth: config.width,
      success: function(compressRes) {
        const compressTime = Date.now() - compressStartTime
        console.log(`图片压缩成功，耗时: ${compressTime}ms`)

        // 获取压缩后的文件信息
        wx.getFileInfo({
          filePath: compressRes.tempFilePath,
          success: function(compressedInfo) {
            const compressedSizeMB = compressedInfo.size / 1024 / 1024
            const ratio = ((1 - compressedInfo.size / (originalSizeMB * 1024 * 1024)) * 100).toFixed(1)
            console.log(`压缩后: ${compressedSizeMB.toFixed(2)}MB, 压缩率: ${ratio}%, 节省: ${(originalSizeMB - compressedSizeMB).toFixed(2)}MB`)
          }
        })

        // 更新状态为上传中
        that.setData({
          loadingText: '正在上传图片...'
        })

        // 使用压缩后的图片上传
        that.doUpload(compressRes.tempFilePath)
      },
      fail: function(err) {
        console.warn('图片压缩失败，使用原图:', err)
        // 压缩失败则使用原图
        that.setData({
          loadingText: '正在上传图片...'
        })
        that.doUpload(imageUrl)
      }
    })
  },

  // 执行实际的上传操作
  doUpload: function(filePath) {
    const that = this
    const uploadStartTime = Date.now()
    let isSuccess = false  // 标记是否成功

    // 定时更新加载进度提示
    const progressTimer1 = setTimeout(() => {
      that.setData({
        loadingText: '正在识别书籍信息...'
      })
    }, 1000)  // 1秒后：识别阶段

    const progressTimer2 = setTimeout(() => {
      that.setData({
        loadingText: '正在搜索豆瓣评分...'
      })
    }, 2500)  // 2.5秒后：搜索豆瓣阶段

    const progressTimer3 = setTimeout(() => {
      that.setData({
        loadingText: '即将完成，请稍候...'
      })
    }, 4500)  // 4.5秒后：即将完成

    wx.uploadFile({
      url: `${app.globalData.apiBaseUrl}/api/recognize-book`,
      filePath: filePath,
      name: 'image',
      timeout: 60000, // 60秒超时
      header: {
        'content-type': 'multipart/form-data'
      },
      success: function(res) {
        const uploadTime = Date.now() - uploadStartTime
        console.log(`图片上传及识别完成，耗时: ${uploadTime}ms`)

        try {
          const data = JSON.parse(res.data)
          if (data.success) {
            isSuccess = true  // 标记成功
          }
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
        // 清除所有定时器
        clearTimeout(progressTimer1)
        clearTimeout(progressTimer2)
        clearTimeout(progressTimer3)

        // 只在失败时关闭loading，成功时保持loading直到页面跳转完成
        if (!isSuccess) {
          that.setData({
            isLoading: false
          })
        }
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
