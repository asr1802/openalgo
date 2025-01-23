from flask import Blueprint, jsonify, request, render_template, session, redirect, url_for
from importlib import import_module
from database.auth_db import get_auth_token
from utils.session import check_session_validity
import logging

logger = logging.getLogger(__name__)

# Define the blueprint
orders_bp = Blueprint('orders_bp', __name__, url_prefix='/')

def dynamic_import(broker, module_name, function_names):
    module_functions = {}
    try:
        # Import the module based on the broker name
        module = import_module(f'broker.{broker}.{module_name}')
        for name in function_names:
            module_functions[name] = getattr(module, name)
        return module_functions
    except (ImportError, AttributeError) as e:
        logger.error(f"Error importing functions {function_names} from {module_name} for broker {broker}: {e}")
        return None

@orders_bp.route('/orderbook')
@check_session_validity
def orderbook():
    broker = session.get('broker')
    if not broker:
        logger.error("Broker not set in session")
        return "Broker not set in session", 400

    # Dynamically import broker-specific modules for API and mapping
    api_funcs = dynamic_import(broker, 'api.order_api', ['get_order_book'])
    mapping_funcs = dynamic_import(broker, 'mapping.order_data', [
        'calculate_order_statistics', 'map_order_data', 
        'transform_order_data'
    ])

    if not api_funcs or not mapping_funcs:
        logger.error(f"Error loading broker-specific modules for {broker}")
        return "Error loading broker-specific modules", 500

    # Static import used for auth token retrieval
    login_username = session['user']
    auth_token = get_auth_token(login_username)

    if auth_token is None:
        logger.warning(f"No auth token found for user {login_username}")
        return redirect(url_for('auth.logout'))

    order_data = api_funcs['get_order_book'](auth_token)
    logger.debug(f"Order data received: {order_data}")
    
    if 'status' in order_data:
        if order_data['status'] == 'error':
            logger.error("Error in order data response")
            return redirect(url_for('auth.logout'))

    order_data = mapping_funcs['map_order_data'](order_data=order_data)
    order_stats = mapping_funcs['calculate_order_statistics'](order_data)
    order_data = mapping_funcs['transform_order_data'](order_data)

    return render_template('orderbook.html', order_data=order_data, order_stats=order_stats)

@orders_bp.route('/tradebook')
@check_session_validity
def tradebook():
    broker = session.get('broker')
    if not broker:
        logger.error("Broker not set in session")
        return "Broker not set in session", 400

    # Dynamically import broker-specific modules for API and mapping
    api_funcs = dynamic_import(broker, 'api.order_api', ['get_trade_book'])
    mapping_funcs = dynamic_import(broker, 'mapping.order_data', [
        'map_trade_data', 'transform_tradebook_data'
    ])

    if not api_funcs or not mapping_funcs:
        logger.error(f"Error loading broker-specific modules for {broker}")
        return "Error loading broker-specific modules", 500

    login_username = session['user']
    auth_token = get_auth_token(login_username)

    if auth_token is None:
        logger.warning(f"No auth token found for user {login_username}")
        return redirect(url_for('auth.logout'))

    # Using the dynamically imported `get_trade_book` function
    get_trade_book = api_funcs['get_trade_book']
    tradebook_data = get_trade_book(auth_token)
    logger.debug(f"Tradebook data received: {tradebook_data}")
  
    if 'status' in tradebook_data and tradebook_data['status'] == 'error':
        logger.error("Error in tradebook data response")
        return redirect(url_for('auth.logout'))

    # Using the dynamically imported mapping functions
    map_trade_data = mapping_funcs['map_trade_data']
    transform_tradebook_data = mapping_funcs['transform_tradebook_data']

    tradebook_data = map_trade_data(trade_data=tradebook_data)
    tradebook_data = transform_tradebook_data(tradebook_data)

    return render_template('tradebook.html', tradebook_data=tradebook_data)

@orders_bp.route('/positions')
@check_session_validity
def positions():
    broker = session.get('broker')
    if not broker:
        logger.error("Broker not set in session")
        return "Broker not set in session", 400

    # Dynamically import broker-specific modules for API and mapping
    api_funcs = dynamic_import(broker, 'api.order_api', ['get_positions'])
    mapping_funcs = dynamic_import(broker, 'mapping.order_data', [
        'map_position_data', 'transform_positions_data'
    ])

    if not api_funcs or not mapping_funcs:
        logger.error(f"Error loading broker-specific modules for {broker}")
        return "Error loading broker-specific modules", 500

    login_username = session['user']
    auth_token = get_auth_token(login_username)

    if auth_token is None:
        logger.warning(f"No auth token found for user {login_username}")
        return redirect(url_for('auth.logout'))

    # Using the dynamically imported `get_positions` function
    get_positions = api_funcs['get_positions']
    positions_data = get_positions(auth_token)
    logger.debug(f"Positions data received: {positions_data}")
   
    if 'status' in positions_data and positions_data['status'] == 'error':
        logger.error("Error in positions data response")
        return redirect(url_for('auth.logout'))

    # Using the dynamically imported mapping functions
    map_position_data = mapping_funcs['map_position_data']
    transform_positions_data = mapping_funcs['transform_positions_data']

    positions_data = map_position_data(positions_data)
    positions_data = transform_positions_data(positions_data)
    
    return render_template('positions.html', positions_data=positions_data)

@orders_bp.route('/darvas')
@check_session_validity
def darvas():
    broker = session.get('broker')
    if not broker:
        logger.error("Broker not set in session")
        return "Broker not set in session", 400

    # Dynamically import broker-specific modules for API and mapping
    api_funcs = dynamic_import(broker, 'api.darvas', ['get_data'])
    mapping_funcs = dynamic_import(broker, 'mapping.order_data', ['calculate_darvas_statistics'])

    if not api_funcs or not mapping_funcs:
        logger.error(f"Error loading broker-specific modules for {broker}")
        return "Error loading broker-specific modules", 500

    login_username = session['user']
    auth_token = get_auth_token(login_username)

    if auth_token is None:
        logger.warning(f"No auth token found for user {login_username}")
        return redirect(url_for('auth.logout'))

    # Using the dynamically imported `get_positions` function
    get_data = api_funcs['get_data']
    darvas_data = get_data(auth_token)
    logger.debug(f"Darvas data received: {darvas_data}")
    # print(darvas_data)
    # if 'status' in darvas_data and darvas_data['status'] == 'error':
    #     logger.error("Error in Darvas data response")
    #     return redirect(url_for('auth.logout'))

    # # Using the dynamically imported mapping functions
    # map_position_data = mapping_funcs['map_position_data']
    # transform_positions_data = mapping_funcs['transform_darvas_data']
    calculate_darvas_statistics = mapping_funcs['calculate_darvas_statistics']
    # positions_data = map_position_data(positions_data)
    # darvas_data = transform_positions_data(darvas_data)
    portfolio_stats = calculate_darvas_statistics(darvas_data)
    
    return render_template('darvas.html', darvas_data=darvas_data,portfolio_stats=portfolio_stats)


@orders_bp.route('/holdings')
@check_session_validity
def holdings():
    broker = session.get('broker')
    if not broker:
        logger.error("Broker not set in session")
        return "Broker not set in session", 400

    # Dynamically import broker-specific modules for API and mapping
    api_funcs = dynamic_import(broker, 'api.order_api', ['get_holdings'])
    mapping_funcs = dynamic_import(broker, 'mapping.order_data', [
        'map_portfolio_data', 'calculate_portfolio_statistics', 'transform_holdings_data'
    ])

    if not api_funcs or not mapping_funcs:
        logger.error(f"Error loading broker-specific modules for {broker}")
        return "Error loading broker-specific modules", 500

    login_username = session['user']
    auth_token = get_auth_token(login_username)

    if auth_token is None:
        logger.warning(f"No auth token found for user {login_username}")
        return redirect(url_for('auth.logout'))

    # Using the dynamically imported `get_holdings` function
    get_holdings = api_funcs['get_holdings']
    holdings_data = get_holdings(auth_token)
    logger.debug(f"Holdings data received: {holdings_data}")

    if 'status' in holdings_data and holdings_data['status'] == 'error':
        logger.error("Error in holdings data response")
        return redirect(url_for('auth.logout'))

    # Using the dynamically imported mapping functions
    map_portfolio_data = mapping_funcs['map_portfolio_data']
    calculate_portfolio_statistics = mapping_funcs['calculate_portfolio_statistics']
    transform_holdings_data = mapping_funcs['transform_holdings_data']

    holdings_data = map_portfolio_data(holdings_data)
    portfolio_stats = calculate_portfolio_statistics(holdings_data)
    holdings_data = transform_holdings_data(holdings_data)
    
    return render_template('holdings.html', holdings_data=holdings_data, portfolio_stats=portfolio_stats)
