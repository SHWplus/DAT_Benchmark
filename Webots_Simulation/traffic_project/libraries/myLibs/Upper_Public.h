#pragma once


typedef struct _Fit_Params
{
    double a = 0;
    double b = 0;
    double c = 0;
    double d = 0;
}Fit_Params;

namespace upper
{
    template<typename F, typename F1>
    F constrain(F input, F1 threshold)
    {
        if (threshold < 0)
            threshold = -threshold;

        if (input <= -threshold)
            return -threshold;
        else if (input >= threshold)
            return threshold;

        return input;
    }

    template<typename F, typename F1>
    F constrain(F input, F1 threshold_1, F1 threshold_2)
    {
        F min, max;
        if (threshold_1 > threshold_2)
        {
            max = threshold_1;
            min = threshold_2;
        }
        else
        {
            min = threshold_1;
            max = threshold_2;
        }

        if (input <= min)
            return min;
        else if (input >= max)
            return max;
        return input;
    }
}