#pragma once
#include "Timer.h"

#include <cstdio>
#include <cstring>
#include <string>
#include <iostream>
#include <cstdint>
#include <cmath>

const uint32_t MAX_USER_ID = 519173547;

struct Index_note
{
    Index_note() {}
    Index_note(uint64_t pos) : pos_(pos), group_count_(0) {}
    uint64_t pos_;
    uint32_t group_count_;
};

struct Pair_note
{
    uint32_t user_;
    uint32_t group_;
};

struct sparse_vector
{
    sparse_vector(size_t len) : len_(len), data_(new uint32_t[len]) {}
    ~sparse_vector() {delete[] data_;}

    uint32_t& operator[](size_t ind) {return data_[ind];}

    double cosine_dist(const sparse_vector* rv)
    {
        if (rv == nullptr)
            return 0;
        
        size_t ind1 = 0;
        size_t ind2 = 0;

        double cross = 0;

        while ((ind1 != this->len_) && (ind2 != rv->len_))
        {
            if (this->data_[ind1] > rv->data_[ind2])
                ++ind2;
            else if (this->data_[ind1] < rv->data_[ind2])
                ++ind1;
            else
            {
                ++cross;
                ++ind1;
                ++ind2;
            }
        }

        return cross / (sqrt(this->len_) * sqrt(rv->len_));
    }

    size_t len_;
    uint32_t* data_;
};

sparse_vector* get_info(uint32_t id, FILE* index_table, FILE* group_list)
{
    sparse_vector* ans = nullptr;

    fseeko64(index_table, (uint64_t)id * sizeof(Index_note), SEEK_SET);

    Index_note index_note;

    fread(&index_note, sizeof(index_note), 1, index_table);

    if (index_note.group_count_ > 0)
    {
        ans = new sparse_vector(index_note.group_count_);

        fseeko64(group_list, index_note.pos_ * sizeof(uint32_t), SEEK_SET);

        fread(ans->data_, sizeof(uint32_t), index_note.group_count_, group_list);

        return ans;
    }
    else
        return nullptr;
}

sparse_vector* get_info_guess(uint32_t id, FILE* index_table, FILE* group_list)
{
    sparse_vector* ans = nullptr;

    Index_note index_note;

    fread(&index_note, sizeof(index_note), 1, index_table);

    if (index_note.group_count_ > 0)
    {
        ans = new sparse_vector(index_note.group_count_);

        fread(ans->data_, sizeof(uint32_t), index_note.group_count_, group_list);

        return ans;
    }
    else
        return nullptr;
}