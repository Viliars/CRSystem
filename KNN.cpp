#include "functions.h"
#include <queue>
#include <set>
#include <map>
#include <algorithm>


std::vector<uint32_t> predict_users(uint32_t predict_id, FILE* index_table, FILE* group_list,\
                                        size_t n_users = 10)
{
    std::vector<uint32_t> predict;

    auto predict_vec = get_info(predict_id, index_table, group_list);
    if (predict_vec == nullptr)
        return predict;

    rewind(index_table);
    rewind(group_list);

    using user_dist = std::pair<uint32_t, double>;

    auto cmp = [](user_dist a, user_dist b) { return a.second > b.second; };
    std::priority_queue<user_dist, std::vector<user_dist>, decltype(cmp)> top(cmp);

    for (uint32_t user_id = 0; user_id <= MAX_USER_ID; ++user_id)
    {
        sparse_vector* compare_vec = get_info_guess(user_id, index_table, group_list);

        if (user_id == predict_id)
        {
            delete compare_vec;
            continue;
        }

        if (compare_vec != nullptr)
        {
            double dist = predict_vec->cosine_dist(compare_vec);

            if (dist > 0)
            {
                if (top.size() < n_users)
                    top.push({user_id, dist});
                else if (dist > top.top().second)
                {
                    top.pop();
                    top.push({user_id, dist});
                }
            }

            delete compare_vec;
        }
    }

    while (top.size())
    {
        predict.push_back(top.top().first);
        top.pop();
    }

    delete predict_vec;

    return predict;
}

std::vector<uint32_t> predict_groups(uint32_t id, const std::vector<uint32_t> &neighbours,\
                                        FILE* index_table, FILE* group_list, size_t n_groups=20)
{
    std::map<uint32_t, uint32_t> counter;

    for (auto item : neighbours)
    {
        auto item_vec = get_info(item, index_table, group_list);

        for (size_t ind = 0; ind < item_vec->len_; ++ind)
            counter[item_vec->data_[ind]]++;

        delete item_vec;
    }

    auto id_vec = get_info(id, index_table, group_list);

    for (size_t ind = 0; ind < id_vec->len_; ++ind)
        counter[id_vec->data_[ind]] = 0;

    delete id_vec;

    std::vector<std::pair<uint32_t, uint32_t>> pre_ans;
    for (auto item : counter)
        if (item.second > 0)
            pre_ans.push_back(item);

    auto cmp = [](std::pair<uint32_t, uint32_t> a, std::pair<uint32_t, uint32_t> b) 
    {
        return a.second > b.second;
    };

    std::sort(pre_ans.begin(), pre_ans.end(), cmp);

    std::vector<uint32_t> ans;
    for (size_t ind; ind < n_groups && ind < pre_ans.size(); ++ind)
        ans.push_back(pre_ans[ind].first);

    return ans;
}

int main()
{
    Timer T;
    FILE* index_table = fopen("/mnt/sda6/Data/CRSystem/subscribers.ind", "rb");
    FILE* group_list = fopen("/mnt/sda6/Data/CRSystem/subscribers.dat", "rb");

    auto usr = predict_users(116761932, index_table, group_list);
    auto ans = predict_groups(116761932, usr, index_table, group_list);

    for (auto item : ans)
        std::cout << item << std::endl;

    fclose(group_list);
    fclose(index_table);
    return 0;
}