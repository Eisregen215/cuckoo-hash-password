import hashlib
import string
import random
import time

class Node:
    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.next = None

class CuckooHash:
    def __init__(self, size):
        self.hashArray1 = [None] * size
        self.hashArray2 = [None] * size
        self.numKeys = 0
        self.singleList = SingleLinkedList()

    def __len__(self):
        return self.numKeys

    def __hashFunc(self, s):
        telephone = s.encode('utf-8')
        v1 = hashlib.sha256()
        v1.update(telephone)
        password = v1.hexdigest()
        h1 = int(password[:32], 16) % len(self.hashArray1)
        h2 = int(password[32:], 16) % len(self.hashArray1)
        return h1, h2

    def find(self, key):
        self.find_count += 1  # 记录查找次数
        bucket1, bucket2 = self.__hashFunc(key)
        if self.hashArray1[bucket1] and self.hashArray1[bucket1].key == key:
            return self.hashArray1[bucket1].data
        elif self.hashArray2[bucket2] and self.hashArray2[bucket2].key == key:
            return self.hashArray2[bucket2].data
        else:
            return self.singleList.search(key)

    def delete(self, key):
        self.delete_count += 1  # 记录删除次数
        if self.find(key) is None:
            return False
        bucket1, bucket2 = self.__hashFunc(key)
        if self.hashArray1[bucket1] and self.hashArray1[bucket1].key == key:
            self.hashArray1[bucket1] = None
            self.numKeys -= 1
        elif self.hashArray2[bucket2] and self.hashArray2[bucket2].key == key:
            self.hashArray2[bucket2] = None
            self.numKeys -= 1
        else:
            self.singleList.remove(key)
        return True

    def insert(self, key, data):
        self.insert_count += 1  # 记录插入次数
        if self.find(key) is not None:
            return False
        count = 0
        while count < 500:
            bucket1, bucket2 = self.__hashFunc(key)
            if self.hashArray1[bucket1] is None:
                newNode = Node(key, data)
                self.hashArray1[bucket1] = newNode
                self.numKeys += 1
                return True
            elif self.hashArray2[bucket2] is None:
                newNode = Node(key, data)
                self.hashArray2[bucket2] = newNode
                self.numKeys += 1
                return True
            else:
                # Kick out an element and re-insert it
                if count % 2 == 0:
                    kickedNode = self.hashArray1[bucket1]
                    self.hashArray1[bucket1] = Node(key, data)
                    key, data = kickedNode.key, kickedNode.data
                else:
                    kickedNode = self.hashArray2[bucket2]
                    self.hashArray2[bucket2] = Node(key, data)
                    key, data = kickedNode.key, kickedNode.data
                count += 1
                self.insert_count += 1  # 计入重新插入的次数
        # Insert into single linked list on infinite loop
        self.singleList.append(key, data)
        return True

class SingleLinkedList:
    def __init__(self):
        self.head = None

    def append(self, key, data):
        newNode = Node(key, data)
        if not self.head:
            self.head = newNode
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = newNode

    def search(self, key):
        cur = self.head
        while cur:
            self.find_count += 1  # 单链表查找也要计数
            if cur.key == key:
                return cur.data
            cur = cur.next
        return None

    def remove(self, key):
        cur = self.head
        pre = None
        while cur:
            self.delete_count += 1  # 单链表删除也要计数
            if cur.key == key:
                if pre:
                    pre.next = cur.next
                else:
                    self.head = cur.next
                return True
            pre = cur
            cur = cur.next
        return False

def __test():
    alpha = 1  # 预支空间的倍数
    cuckoo_hash = CuckooHash(alpha * 25000)
    # 确保每次测试开始时计数器清零
    cuckoo_hash.find_count = 0
    cuckoo_hash.delete_count = 0
    cuckoo_hash.insert_count_kicks = 0  # 新增计数器，用于记录踢出操作次数

    with open('hash1.txt', 'r', encoding='utf-8') as f:
        insert_data = [line.strip().split()[1:] for line in f.readlines()]
    with open('hash3.txt', 'r', encoding='utf-8') as f:
        query_delete_data = [line.strip().split()[1:] for line in f.readlines()]

    # 插入测试
    start_time = time.time()
    for key, *data in insert_data:
        if not cuckoo_hash.insert(key, ' '.join(data)):
            # 如果插入失败（即发生踢出操作），增加踢出操作计数
            cuckoo_hash.insert_count_kicks += 1
    insert_time = time.time() - start_time
    # 考虑踢出操作，计算真实的插入访问内存次数
    total_insert_accesses = cuckoo_hash.insert_count + cuckoo_hash.insert_count_kicks
    insert_cost_rate = total_insert_accesses / len(insert_data)

    # 查找测试
    for key in [kd[0] for kd in query_delete_data]:
        _ = cuckoo_hash.find(key)
    find_cost_rate = cuckoo_hash.find_count / len(query_delete_data)

    # 删除测试
    for key in [kd[0] for kd in query_delete_data]:
        _ = cuckoo_hash.delete(key)
    delete_cost_rate = cuckoo_hash.delete_count / len(query_delete_data)

    death_factor = len(cuckoo_hash.singleList) / len(insert_data)

    print(f"Death_factor={death_factor}")
    print(f"Insert_cost_rate={insert_cost_rate:.2f}")  # 保留两位小数输出
    print(f"Find_cost_rate={find_cost_rate:.2f}")
    print(f"Delete_cost_rate={delete_cost_rate:.2f}")

#__test()