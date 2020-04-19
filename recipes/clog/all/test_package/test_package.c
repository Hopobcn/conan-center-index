#include <clog.h>

CLOG_DEFINE_LOG_INFO(named_log_info, "Clog test_package", CLOG_INFO);

int main()
{
    named_log_info("If you see this, clog works.\nPASS");
    return 0;
}