Title: Wordpress comment form with bootstrap v3.0.2
Date: 2013-11-08 10:36
Author: Nikolai Tschacher
Category: Programming
Tags: Bootstrap, Comment, Programming, Form, Wordpress
Slug: wordpress-comment-form-with-bootstrap-v3-0-2
Status: published

Hey everybody!

In this short article I will explain how I designed my wordpress theme's
comment section with bootstrap 3.0.2. For the most recent changes, you
find my [theme on github](https://github.com/NikolaiT/clearcontent/). If
you want to see a live demo, just inspect the comment form on this site.
It uses exactly this bootstrap styled form I am discussing here.

In order to follow the content's of this blog post, you should have
basic experience with PHP and HTML/CSS.

### The Problem

The tricky question here is, whether we can use a action or filter hook
to manipulate the comment form to our liking, or if we have to use and
modify the original `comment_form()` function directly. Our goal is to
decorate the form with some bootstrap widget classes and use the
bootstrap grid layout. We want to obtain a horizontal form, such as
demonstrated [here](http://getbootstrap.com/css/#forms-horizontal).
After a quick search, I found the function [`comment_form( $args,
$post_id);`](http://codex.wordpress.org/Function_Reference/comment_form) in the
wordpress codex. While it looks promising on the first glimpse, some
hindrances become clear after further thinking through. The function's
description says:

> Most strings and form fields may be controlled through the $args
> array passed into the function, while you may also choose to use the
> `comment_form_default_fields` filter to modify the array of default
> fields if you'd just like to add a new one or remove a single field.
> All fields are also individually passed through a filter of the form
> `comment_form_field_$name` where `$name` is the key used in the array
> of fields.
>
> <small>Wordpress codex at
> <http://codex.wordpress.org/Function_Reference/comment_form>

But there are two html elements in the function that aren't passed
through any filters/actions: The `<form\>` element itself (With the
bootstrap comment form applied, the `<form\>` element should be `<form
class="form-horizontal" role="form"\>`) and the submit button that needs
to be wrapped in the following div element:

    <div class="form-group">
    </div>

Therefore we can't achieve the bootstrap horizontal comment form with
passing modified `$args to comment_form()` template.

### A Solution


My quick & dirty solution was to just copy the `comment_form()` code from
[comment-template.php](http://core.trac.wordpress.org/browser/tags/3.7.1/src/wp-includes/comment-template.php#L1509),
incorporate it in our theme (within functions.php for example) and then
modify it directly to our liking. I guess that doing so is
controversial, because there might be other ways to style the elements
that aren't affected by any filters. For instance, if we can't modify
the `<form\>` attribute with the boostrap class "form-horizontal", we
could alternatively just wrap the whole `comment_form()` within a div
element of the same class (Not tested if it really works though).

Anyways, my modified `comment_form` template can be found
[here](https://github.com/NikolaiT/clearcontent/blob/master/inc/template-tags.php)
under the name `clearcontent_comment_form()`.

The solution is not really nice, because it violates the good wordpress
design pattern, namely avoiding duplicate code with hooks. The
disadvantage is the the potential inconsistency with the real
`comment_form()` code: Whenever wordpress updates, I need to change my
custom `comment_form()` too in order to make sure the interfaces stays
stable that `comment_form()` provides. This is very inconvenient to say
the least.
