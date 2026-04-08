#include "rtapi.h"
#include "rtapi_app.h"
#include "hal.h"

#include "RP1/rp1lib.h"
#include "RP1/rp1lib.c"
#include "RP1/gpiochip_rp1.h"
#include "RP1/gpiochip_rp1.c"

#define COMPONENT_NAME "rp1"

/* Component ID */
static int comp_id;

/* Component initialization */
int rtapi_app_main(void)
{
    comp_id = hal_init(COMPONENT_NAME);
    if (comp_id < 0)
    {
        rtapi_print_msg(RTAPI_MSG_ERR,
                        "%s: Failed to initialize HAL component\n",
                        COMPONENT_NAME);
        return comp_id;
    }


        hal_ready(comp_id);
    return 0;

error:

    rtapi_print_msg(RTAPI_MSG_ERR, "init STM32 Error \n");
    hal_exit(comp_id);
    return 0;
}

/* Component cleanup */
void rtapi_app_exit(void)
{
    // Clean up HAL
    hal_exit(comp_id);
}