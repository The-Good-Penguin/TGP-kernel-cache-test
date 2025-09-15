/******************************************************************************
 *
 *   Copyright (C) 2011  Intel Corporation. All rights reserved.
 *
 *   This program is free software;  you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; version 2 of the License.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY;  without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
 *   the GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program;  if not, write to the Free Software
 *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 *
 *****************************************************************************/

#include <linux/module.h>
#include <linux/bootcache.h>

#define DRIVER_NAME "bootcache_tester"

typedef union {
    u8 val_u8;
    u16 val_u16;
    u32 val_u32;
	u64 val_u64;
    char *val_str;
} value_union;

struct test_data {
	const char *name;
	int type;
	value_union value;
};

#define SIZE_u64 1
#define SIZE_u32 2
#define SIZE_u16 3
#define SIZE_u8 4
#define SIZE_STRING 5


static struct test_data test_data_array[] = {
	{
		.name = "Bootcache Test One",
		.value.val_u32 = 1234,
		.type = SIZE_u32,
	},
	{
		.name = "Bootcache Test Two",
		.value.val_u32 = 5678,
		.type = SIZE_u32,
	},
	{
		.name = "Bootcache Test Three",
		.value.val_u32 = 9012,
		.type = SIZE_u32,
	},
	{
		.name = "Bootcache Test Four",
		.value.val_u32 = 0xDEADBEEF,
		.type = SIZE_u32,
	},
	{
		.name = "Bootcache Test Five",
		.value.val_u32 = 0xC0DEBAD0,
		.type = SIZE_u32,
	},
	{
		.name = "u32_key",
		.value.val_u32 = 0xFFFFFFFF,
		.type = SIZE_u32,
	},
	{
		.name = "u16_key",
		.value.val_u16 = 0xFFFF,
		.type = SIZE_u16,
	},
	{
		.name = "u8",
		.value.val_u8 = 0xFF,
		.type = SIZE_u8,
	},
	{
		.name = "string_key",
		.value.val_str = "This is some sample string data.",
		.type = SIZE_STRING,
	},
};

static int __init bootcache_test_init(void)
{
	pr_info("bootcache-test module loading\n");

	/* Test for bootcache variables! */

	int res;
	int i;

	value_union vardata;
	char vardata_str[255];

	vardata.val_str = &vardata_str[0];


	for (i = 0; i < ARRAY_SIZE(test_data_array); i++) {
		bool correct = false;
		switch(test_data_array[i].type)
		{
			case SIZE_u64:
				res = bootcache_get_u64(test_data_array[i].name, &vardata.val_u64);
				if (!res) {
					correct = ( vardata.val_u64 == test_data_array[i].value.val_u64);
					pr_info("%s : %s = 0x%llx\n", DRIVER_NAME, test_data_array[i].name, vardata.val_u64 );
				}
				break;

			case SIZE_u32:
				res = bootcache_get_u32(test_data_array[i].name, &vardata.val_u32);
				if (!res) {
					correct = ( vardata.val_u32 == test_data_array[i].value.val_u32);
					pr_info("%s : %s = 0x%x\n", DRIVER_NAME, test_data_array[i].name, vardata.val_u32 );
				}
				break;

			case SIZE_u16:
				res = bootcache_get_u16(test_data_array[i].name, &vardata.val_u16);
				if (!res) {
					correct = ( vardata.val_u16 == test_data_array[i].value.val_u16);
					pr_info("%s : %s = 0x%x\n", DRIVER_NAME, test_data_array[i].name, vardata.val_u16);
				}
				break;

			case SIZE_u8:
				/*
				res = bootcache_get_u8(test_data_array[i].name, &vardata.val_u8);
				if (!res) {
					correct = ( vardata.val_u8 == test_data_array[i].value.val_u8);
					pr_info("%s : %s = 0x%x\n", DRIVER_NAME, test_data_array[i].name, vardata.val_u8);
				}
				*/
				pr_info("%s : bootcache_get_u8(%s) not supported\n", DRIVER_NAME, test_data_array[i].name);
				res = -1;
				break;

			case SIZE_STRING:
				res = bootcache_get_string(test_data_array[i].name, &vardata_str[0], 254);
				if (!res) {
					correct = ( strcmp(&vardata_str[0], test_data_array[i].value.val_str) == 0);
					pr_info("%s : %s = %s\n", DRIVER_NAME, test_data_array[i].name, &vardata_str[0]);
				}
				break;

			default:
				pr_info("%s: Unknown Type for %s(%d)\n", DRIVER_NAME, test_data_array[i].name,
					test_data_array[i].type);
		}

		if (res)
			pr_info("%s: res for %s = %d\n", DRIVER_NAME, test_data_array[i].name, res);
		else {
			pr_info("%s : %s is %s\n",  DRIVER_NAME, test_data_array[i].name,
				(correct = true) ? "Correct" : "Incorrect");
		}
	}

	/* Test writing variables and reading back */
	pr_info("Testing how to create a variable\n");

	res = bootcache_set_u32("testvar1", 0xDEADBEEF);
	pr_info("%s: res for testvar1 creation = %d\n", DRIVER_NAME, res);

	pr_info("Testing the values read back\n");
	res = bootcache_get_u32("testvar1", &vardata.val_u32);
	pr_info("%s: testvar1 = 0x%x\n", DRIVER_NAME, vardata.val_u32);

	pr_info("Testing changing a variable\n");
	res = bootcache_set_u32("testvar1", 0x55AA55AA);
	pr_info("%s: res for testvar1 change = %d\n", DRIVER_NAME, res);

	pr_info("Testing the values read back\n");
	res = bootcache_get_u32("testvar1", &vardata.val_u32);
	pr_info("%s: testvar1 = 0x%x\n", DRIVER_NAME, vardata.val_u32);

	pr_info("%s : Incremeting testCounter\n", DRIVER_NAME);
	res = bootcache_get_u32("testCounter", &vardata.val_u32);
	if (res)
		res = bootcache_set_u32("testCounter", 0x1);
	else {
		pr_info("%s: Current testCounter = %d\n", DRIVER_NAME, vardata.val_u32);
		pr_info("%s: Incrementing..\n", DRIVER_NAME);
		res = bootcache_set_u32("testCounter", vardata.val_u32+1);
	}
	pr_info("%s : res for testCounter change = %d\n", DRIVER_NAME, res);

	return 0;
}

static void __exit bootcache_test_exit(void)
{
	pr_info("bootcache-test module unloading\n");

}

module_init(bootcache_test_init);
module_exit(bootcache_test_exit);
MODULE_LICENSE("GPL");
