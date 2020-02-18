Title: Hide related products on shop page in Woocommerce
Date: 2018-08-30 17:12
Modified: 2018-08-30 17:12
Author: Nikolai Tschacher
Category: Wordpress, WooCommerce, functions.php, CSS, related-products
Tags: Wordpress, WooCommerce, functions.php, CSS, hide-related-products, disable related products
Slug: wordpress-hide-related-products-in-woocommerce
Status: published

## Introduction

I found many instructions and guides in the Internet that describe **How to hide related products tab on shop page** to be **NOT WORKING!**

It's a freaking pain in the ass to hide your related products tab on your shop page. The method to actually hide related products depends on the WooCommerce theme that you are using. In this article, we are going to present a method that provably works for every theme and WooCommerce version out there.

## How to disable related products - Step by step guide

**Step 1.** Open the product page where your related products are shown. 


**Step 2.** Right click on the HTML with related products and open page inspect. See the picture below.

<img src="/images/related-products-inspect.png" alt="Inspect element"/>


**Step 3.** Copy the class attribute of the container element that contains the related products HTML.

<img src="/images/related-products-copy-class.png" alt="Copy css of container class"/>


**Step 4.** Insert the copied class code to this CSS code. In my case, I copied `related related-products-wrapper product-section` and the resulting CSS will look like this. So you only have to replace spaces `' '` with points `'.'`.

In my case the final CSS code looks like this:

```css
.related.related-products-wrapper.product-section {
	display: none !important;
}
```

**Step 5.** Replace CSS code from above with the line  `{{YOUR CSS CODE HERE}}` in the following file:
```php
add_action( 'wp_footer', 'incolumitas_add_inline_script' );
function incolumitas_add_inline_script() {
	?>
	<style type="text/css">
		{{YOUR CSS CODE HERE}}
	</style>
	<?php
}
```

**Step 6.** Finally paste the resulting code at the end of your themes `functions.php`. In my case I needed to paste the following code at the end of my `functions.php`:
```php
add_action( 'wp_footer', 'incolumitas_add_inline_script' );
function incolumitas_add_inline_script() {
	?>
	<style type="text/css">
		.related.related-products-wrapper.product-section {
			display: none !important;
		}
	</style>
	<?php
}
```

You can edit your `functions.php` in the admin menu under **Appearance -> Editor**.


### Pro tip: If you you use Autooptimize plugin

You need to delete the cache of the Autooptimize plugin for the changes to work!


Let me know whether this instruction worked for you.