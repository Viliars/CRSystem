#include "functions.h"
#include <set>
#include <sstream>

int main()
{
    const size_t BUFF_SIZE = 1000;
    Timer T;

    size_t N_FILE = 18;
    FILE* pair_table[N_FILE];

    for (size_t ind = 0; ind < N_FILE; ind++)
    {
        std::stringstream temp;
        if (ind / 10 == 0)
            temp << "/mnt/sda6/Data/CRSystem/responses0" << ind << "_lil";
        else
            temp << "/mnt/sda6/Data/CRSystem/responses" << ind << "_lil";

        pair_table[ind] = fopen(temp.str().c_str(), "rb");
    }
    

    Pair_note pair_note_buf[N_FILE][BUFF_SIZE];
    size_t cur_ind[N_FILE];
    size_t true_size[N_FILE];

    for (size_t ind = 0; ind < N_FILE; ind++)
    {
        cur_ind[ind] = 0;
        true_size[ind] = fread(pair_note_buf[ind], sizeof(Pair_note), BUFF_SIZE, pair_table[ind]);
    }

    FILE* index_table = fopen("/mnt/sda6/Data/CRSystem/subscribers.ind", "wb");
    FILE* group_list = fopen("/mnt/sda6/Data/CRSystem/subscribers.dat", "wb");

    uint64_t group_list_pos = 0;
    for (uint32_t user_id = 0; user_id <= MAX_USER_ID; ++user_id)
    {
        Index_note index_note(group_list_pos);

        std::set<uint32_t> group_set;
        for (size_t batch_ind = 0; batch_ind < N_FILE; batch_ind++)
        {
            while (pair_note_buf[batch_ind][cur_ind[batch_ind]].user_ == user_id && !feof(pair_table[batch_ind]))
            {
                group_set.insert(pair_note_buf[batch_ind][cur_ind[batch_ind]].group_);

                ++cur_ind[batch_ind];
                if (cur_ind[batch_ind] == true_size[batch_ind])
                {
                    true_size[batch_ind] = fread(pair_note_buf[batch_ind], sizeof(Pair_note), BUFF_SIZE, pair_table[batch_ind]);
                    cur_ind[batch_ind] = 0;
                }
            }
        }


        index_note.group_count_ = group_set.size();
        group_list_pos += group_set.size();
        for (auto iter : group_set)
            fwrite(&iter, sizeof(iter), 1, group_list);

        fwrite(&index_note, sizeof(index_note), 1, index_table);
    }


    fclose(group_list);
    fclose(index_table);
    for (size_t ind = 0; ind < N_FILE; ind++)
        fclose(pair_table[ind]);

    return 0;
}