#!/usr/bin/env python3
"""
GitHub Action script for MiMotion step syncing
支持通过环境变量配置的小米运动步数同步脚本
"""

import os
import sys
import json
import random
import logging
from datetime import datetime
import pytz
from mimotion_standalone import MiMotion

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def get_current_step_range(min_step, max_step, hour=None):
    """根据当前时间获取步数范围"""
    if hour is None:
        hour = datetime.now(pytz.timezone('Asia/Shanghai')).hour
    
    # 计算时间进度率 (22点达到最大值)
    time_rate = min(hour / 22, 1)
    
    current_min = int(time_rate * min_step)
    current_max = int(time_rate * max_step)
    
    return current_min, current_max


def sync_account_steps(account_config):
    """同步单个账号的步数"""
    try:
        mi_user = account_config['mi_user']
        mi_password = account_config['mi_password']
        min_step = account_config.get('min_step', 18000)
        max_step = account_config.get('max_step', 25000)
        sync_start_hour = account_config.get('sync_start_hour', 8)
        sync_end_hour = account_config.get('sync_end_hour', 22)
        
        # 检查是否在同步时间范围内
        current_hour = datetime.now(pytz.timezone('Asia/Shanghai')).hour
        if not (sync_start_hour <= current_hour <= sync_end_hour):
            logger.info(f"账号 {mi_user} 不在同步时间范围内 ({sync_start_hour}-{sync_end_hour})")
            return True
        
        # 计算当前应该的步数范围
        current_min, current_max = get_current_step_range(min_step, max_step, current_hour)
        step_count = random.randint(current_min, current_max)
        
        logger.info(f"开始同步账号 {mi_user}，目标步数: {step_count}")
        
        # 执行步数同步
        mi_motion = MiMotion(mi_user, mi_password)
        message, status = mi_motion.sync_step(step_count)
        
        if status:
            logger.info(f"账号 {mi_user} 同步成功: {message}")
        else:
            logger.error(f"账号 {mi_user} 同步失败: {message}")
        
        return status
        
    except Exception as e:
        logger.error(f"同步账号 {account_config.get('mi_user', 'unknown')} 时发生异常: {str(e)}")
        return False


def load_config():
    """从环境变量加载配置"""
    accounts = []
    
    # 方式1: 从单个JSON环境变量加载多个账号
    accounts_json = os.getenv('MI_ACCOUNTS_JSON')
    if accounts_json:
        try:
            accounts_data = json.loads(accounts_json)
            for account_data in accounts_data:
                accounts.append(account_data)
            logger.info(f"从 MI_ACCOUNTS_JSON 加载了 {len(accounts)} 个账号")
        except json.JSONDecodeError as e:
            logger.error(f"解析 MI_ACCOUNTS_JSON 失败: {e}")
            sys.exit(1)
    
    # 方式2: 从单独的环境变量加载单个账号
    mi_user = os.getenv('MI_USER')
    mi_password = os.getenv('MI_PASSWORD')
    
    if mi_user and mi_password:
        account_config = {
            'mi_user': mi_user,
            'mi_password': mi_password,
            'min_step': int(os.getenv('MIN_STEP', '18000')),
            'max_step': int(os.getenv('MAX_STEP', '25000')),
            'sync_start_hour': int(os.getenv('SYNC_START_HOUR', '8')),
            'sync_end_hour': int(os.getenv('SYNC_END_HOUR', '22'))
        }
        accounts.append(account_config)
        logger.info("从单独环境变量加载了 1 个账号")
    
    if not accounts:
        logger.error("未找到账号配置！请设置 MI_ACCOUNTS_JSON 或 MI_USER/MI_PASSWORD 环境变量")
        sys.exit(1)
    
    return accounts


def main():
    """主函数"""
    logger.info("=== MiMotion GitHub Action 步数同步开始 ===")
    
    # 显示当前时间
    current_time = datetime.now(pytz.timezone('Asia/Shanghai'))
    logger.info(f"当前北京时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载配置
    accounts = load_config()
    
    # 同步所有账号
    success_count = 0
    total_count = len(accounts)
    
    for i, account_config in enumerate(accounts, 1):
        logger.info(f"--- 同步第 {i}/{total_count} 个账号 ---")
        if sync_account_steps(account_config):
            success_count += 1
    
    # 输出结果
    logger.info(f"=== 同步完成: {success_count}/{total_count} 个账号成功 ===")
    
    # 如果有账号同步失败，以非零状态码退出
    if success_count < total_count:
        logger.error(f"有 {total_count - success_count} 个账号同步失败")
        sys.exit(1)
    
    logger.info("所有账号同步成功！")


if __name__ == '__main__':
    main()