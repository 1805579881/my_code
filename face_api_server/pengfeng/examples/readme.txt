测试时用ip和端口号访问，正式部署时应该会有正式的域名，假设ip为127.0.0.1，端口号为8000。
1. 调用增量更新接口
（1）版本号为一个非负整数，数字越大代表版本越新，如10。
（2）发送HTTP的GET请求到http://127.0.0.1:8000/sync/face/，参数只有current_version，内容如（1）所述，如果没有current_version则返回全部数据。最终的请求例如http://127.0.0.1:8000/sync/face/?current_version=10
（3）得到的响应如update_is_latest.json和updated.json两个文件所示，第一个文件为当前版本已经是最新，不需要更新；第二个文件代表数据有更新。
（4）返回的结果中，error表示是否出错；is_latest为True表示已经是最新版本，不需要更新，否则进行更新；
（5）当需要进行增量更新时，clear为False；当版本差异过大时，直接整体更新，clear为True，此时会有全部的数据以created的形式传输过来，建议清空一下Android数据。
（6）得到的响应中的current_version代表了服务器目前的最新版本。
2. 记录上传接口
（1）上传数据时，时间直接转换为UNIX时间戳，例如1531201413。
（2）发送HTTP的POST请求到http://127.0.0.1:8000/sync/record/，数据格式如upload_records.json所示，但是在发送POST请求时，根据不同的Content-Type，发送的内容有所不同：
    1)（正常）Content-Type为multipart/form-data
        a) 将upload_records.json中的内容进行序列化，生成一串UTF-8编码的字符串records_string。
        b) POST请求发送的数据为
        {
        "data":records_string
        }
        例如某一次POST请求的数据为：
        {
            "data":'{"device_info": "单元测试设备", "records": {"2e77ae02-85d0-11e8-ab9e-8cec4b81bd8a": [1531398981.440939, 1531398981.4409394]}}'
        }
    2)（简化）Content-Type为application/json
    直接发送下面这种（与upload_records.json中的内容相同）POST请求即可。
    {
        "device_info": "设备详细信息",
        "records": {
        "43b72e63-99aa-49a6-a06c-c9e675abd23c": [
              1531201893,
              1531201909,
              1531201918
            ],
        "bffa64d5-4e0c-4e71-8062-a405e2d50d3c": [
              1531201413,
              1531201415,
              1531201619
            ],
        "debe7627-49d1-47f7-b3c3-a977f0ea075e": [
              1531200581,
              1531200582,
              1531200583
            ]
        }
    }
（3）上传成功后，结果如upload_result.json所示；上传出错，结果如upload_error所示。基本就是判断error是否为真。