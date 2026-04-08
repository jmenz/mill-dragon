#include "rtapi.h"
#include "rtapi_app.h"
#include "hal.h"

#include "RP1/rp1lib.h"
#include "RP1/rp1lib.c"
#include "RP1/gpiochip_rp1.h"
#include "RP1/gpiochip_rp1.c"
#include "RP1/spi-dw.h"
#include "RP1/spi-dw.c"

#define COMPONENT_NAME "rp1"
#define TEST_PIN 26

/* Component ID */
static int comp_id;

typedef struct {
    hal_bit_t *test_input_pin;
} rp1_data_t;

static rp1_data_t *rp1_data;

static void update(void *arg, long period)
{
    int level = gpio_get_level(TEST_PIN);
    
    if (level >= 0) {
        *(rp1_data->test_input_pin) = level;
    }
}

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
    
    // Allocate shared memory for the component data
    rp1_data = hal_malloc(sizeof(rp1_data_t));
    if (!rp1_data) {
        rtapi_print_msg(RTAPI_MSG_ERR, "%s: Failed to allocate shared memory\n", COMPONENT_NAME);
        goto error;
    }

    if (rp1lib_init() < 0) {
        rtapi_print_msg(RTAPI_MSG_ERR, "%s: Failed to init RP1 /dev/mem mapping.\n", COMPONENT_NAME);
        goto error;
    }

    // Configure the GPIO pin as an INPUT
    gpio_set_fsel(TEST_PIN, GPIO_FSEL_INPUT);

    // Create the HAL pin. Now &rp1_data->test_input_pin points to valid shared memory!
    if (hal_pin_bit_newf(HAL_OUT, &(rp1_data->test_input_pin), comp_id, "%s.in-%02d", COMPONENT_NAME, TEST_PIN) < 0) {
        rtapi_print_msg(RTAPI_MSG_ERR, "%s: Failed to create HAL pin\n", COMPONENT_NAME);
        goto error;
    }

    // Export the update function (passing rp1_data as the argument)
    if (hal_export_funct("rp1.update", update, rp1_data, 0, 0, comp_id) < 0) {
        rtapi_print_msg(RTAPI_MSG_ERR, "%s: Failed to export update function\n", COMPONENT_NAME);
        goto error;
    }

    hal_ready(comp_id);
    rtapi_print_msg(RTAPI_MSG_INFO, "%s: Loaded successfully. Monitoring GPIO %d\n", COMPONENT_NAME, TEST_PIN);
    return 0;

error:

    rp1lib_deinit();
    hal_exit(comp_id);
    return -1;
}

/* Component cleanup */
void rtapi_app_exit(void)
{
    // Clean up memory mapping
    rp1lib_deinit();
    
    // Clean up HAL
    hal_exit(comp_id);
    rtapi_print_msg(RTAPI_MSG_INFO, "%s: Exited and memory unmapped\n", COMPONENT_NAME);
}