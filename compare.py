import csv

filtered_item_file = './filtered_item.csv'
compare_item_files = [
    './g_rank/GMarket_1118_9.csv',
    './g_rank/GMarket_1118_10.csv',
    './g_rank/GMarket_1118_11.csv',
    './g_rank/GMarket_1118_14.csv',
    './g_rank/GMarket_1118_15.csv',
    './g_rank/GMarket_1118_18.csv',
    './g_rank/GMarket_1118_19.csv'
]


class Compare():
    def __init__(self):
        self.origin_items = []
        with open(filtered_item_file, 'r', encoding='utf-8') as f:
            rd = csv.reader(f)
            for row in rd:
                self.origin_items.append(row)
        f.close()

        self.new_items = []
        for file in compare_item_files:
            with open(file, 'r', encoding='utf-8') as f:
                rd = csv.reader(f)
                for row in rd:
                    self.new_items.append(row)
            f.close()

    def compare(self):
        filtered_items_link = []
        for item in self.origin_items:
            try:
                filtered_items_link.append(item[9])
            except:
                break

        for item in self.new_items:
            # 시트에 있는 아이템
            if item[7] in filtered_items_link:
                item_index = filtered_items_link.index(item[7])
                # 이미 한번 판매량 비교한 아이템(중복 아이템)
                if len(self.origin_items[item_index]) > 13:
                    salecount_gap = int(item[5]) - int(self.origin_items[item_index][5])
                    before_gap = int(self.origin_items[item_index][13])
                    if salecount_gap > before_gap:
                        self.origin_items[item_index][13] = salecount_gap
                # 처음 판매량 비교하는 아이템
                else:
                    salecount_gap = int(item[5]) - int(self.origin_items[item_index][5])
                    self.origin_items[item_index].append(salecount_gap)
            # 시트에 없는 아이템
            else:
                self.new_items.remove(item)

    def save(self):
        with open('compared.csv', 'w', encoding='utf-8', newline='') as f:
            wr = csv.writer(f)
            for row in self.origin_items:
                wr.writerow(row)

if __name__ == '__main__':
    cpr = Compare()
    cpr.compare()
    cpr.save()
    print("compare done!!")
