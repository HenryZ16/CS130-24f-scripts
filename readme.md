# 上海科技大学 CS130 操作系统课程自用脚本

运行脚本前，请确保已安装`requirements.txt`中的依赖。

### `check-gitlab.py`

该脚本用于检查学生的提交状况。如果某两次相邻的提交，其提交时间间隔大于7天，则以红色字体输出时间间隔。

#### 用法

Windows：

```shell
python check-gitlab.py <groupId> <commitCnt>
```

Linux:

```shell
python3 check-gitlab.py <groupId> <commitCnt>
```

其中，
- `groupId` 为接受检查的小组编号，为一个整数
- `commitCnt` 为输出的 commit 数量，为一个整数；或`inf`，表示不限制数量