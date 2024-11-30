from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Product, Order, StockTransaction, Category, Supplier
from .forms import ProductForm, OrderForm, CategoryForm, SupplierForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import auth_users, allowed_users
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

# Create your views here.


@login_required(login_url="user-login")
def index(request):
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.customer = request.user
            obj.save()
            return redirect("dashboard-index")
    else:
        form = OrderForm()
    context = {
        "form": form,
        "order": order,
        "product": product,
        "product_count": product_count,
        "order_count": order_count,
        "customer_count": customer_count,
    }
    return render(request, "dashboard/index.html", context)



@login_required(login_url="user-login")
def products(request):
    products = Product.objects.all()  # Fetch all products
    context = {
        'products': products,
    }
    return render(request, 'dashboard/product_list.html', context)


@login_required(login_url="user-login")
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('dashboard-products')
    else:
        form = ProductForm()

    context = {
        'form': form,
    }
    return render(request, 'dashboard/add_product.html', context)


@login_required(login_url="user-login")
def product_detail(request, pk):
    context = {}
    return render(request, "dashboard/products_detail.html", context)


@login_required(login_url="user-login")
@allowed_users(allowed_roles=["Admin"])
def customers(request):
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    context = {
        "customer": customer,
        "customer_count": customer_count,
        "product_count": product_count,
        "order_count": order_count,
    }
    return render(request, "dashboard/customers.html", context)


@login_required(login_url="user-login")
@allowed_users(allowed_roles=["Admin"])
def customer_detail(request, pk):
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    customers = User.objects.get(id=pk)
    context = {
        "customers": customers,
        "customer_count": customer_count,
        "product_count": product_count,
        "order_count": order_count,
    }
    return render(request, "dashboard/customers_detail.html", context)


@login_required(login_url="user-login")
@allowed_users(allowed_roles=["Admin"])
def product_edit(request, pk):
    item = Product.objects.get(id=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("dashboard-products")
    else:
        form = ProductForm(instance=item)
    context = {
        "form": form,
    }
    return render(request, "dashboard/products_edit.html", context)


@login_required(login_url="user-login")
@allowed_users(allowed_roles=["Admin"])
def product_delete(request, pk):
    item = Product.objects.get(id=pk)
    if request.method == "POST":
        item.delete()
        return redirect("dashboard-products")
    context = {"item": item}
    return render(request, "dashboard/products_delete.html", context)


@login_required(login_url="user-login")
def order(request):
    order = Order.objects.all()
    order_count = order.count()
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()

    context = {
        "order": order,
        "customer_count": customer_count,
        "product_count": product_count,
        "order_count": order_count,
    }
    return render(request, "dashboard/order.html", context)


@login_required
def stock_update_page(request):
    return render(request, "dashboard/update_stock.html")

@login_required(login_url="user-login")
@allowed_users(allowed_roles=["Admin", "Staff"])
def stock_update(request):
    products = Product.objects.all()
    stock_transactions = StockTransaction.objects.all()
    product_count = products.count()
    transaction_count = stock_transactions.count()

    if request.method == "POST":
        product_id = request.POST.get("product")
        transaction_type = request.POST.get("transaction_type")
        quantity = int(request.POST.get("quantity"))
        product = get_object_or_404(Product, id=product_id)

        if transaction_type == "REMOVE":
            if product.stock_level >= quantity:
                product.stock_level -= quantity
            else:
                messages.error(request, "Insufficient stock!")
                return redirect("dashboard-stock-update")
        elif transaction_type == "ADD":
            product.stock_level += quantity

        # Save product and transaction
        product.save()
        StockTransaction.objects.create(
            product=product,
            quantity=quantity,
            transaction_type=transaction_type,
            performed_by=request.user,
        )
        messages.success(
            request,
            f"Stock successfully updated: {transaction_type.lower()} {quantity} units of {product.name}.",
        )
        return redirect("dashboard-stock-update")

    context = {
        "products": products,
        "product_count": product_count,
        "transaction_count": transaction_count,
    }
    return render(request, "dashboard/stock_update.html", context)



@login_required(login_url="user-login")
def stock_transaction_list(request):
    # Get all stock transactions, sorted by latest first
    transactions = StockTransaction.objects.all().order_by('-timestamp')
    
    context = {
        'transactions': transactions,  # Pass transactions to the template
    }
    return render(request, 'dashboard/stock_transaction_list.html', context)


@login_required(login_url="user-login")
def categories(request):
    categories = Category.objects.all()  # Fetch all categories
    context = {
        'categories': categories,  # Pass the categories to the template
    }
    return render(request, 'dashboard/category_list.html', context)


@login_required(login_url="user-login")
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('dashboard-categories')  # Redirect back to categories list
    else:
        form = CategoryForm()

    context = {
        'form': form,
    }
    return render(request, 'dashboard/add_category.html', context)


@login_required(login_url="user-login")
def edit_category(request, pk):
    category = get_object_or_404(Category, id=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('dashboard-categories')
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'dashboard/edit_category.html', context)



@login_required(login_url="user-login")
def suppliers(request):
    suppliers = Supplier.objects.all()  # Fetch all suppliers
    context = {
        'suppliers': suppliers,
    }
    return render(request, 'dashboard/supplier_list.html', context)


@login_required(login_url="user-login")
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully!')
            return redirect('dashboard-suppliers')
    else:
        form = SupplierForm()

    context = {
        'form': form,
    }
    return render(request, 'dashboard/add_supplier.html', context)
