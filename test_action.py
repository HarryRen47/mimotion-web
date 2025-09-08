#!/usr/bin/env python3
"""
Test script for the GitHub Action implementation
测试 GitHub Action 实现的脚本
"""

import os
import sys

# Test environment variables
def test_environment_setup():
    """Test environment variable configuration"""
    print("=== 环境变量配置测试 ===")
    
    # Test single account setup
    os.environ['MI_USER'] = 'test_user'
    os.environ['MI_PASSWORD'] = 'test_password'
    os.environ['MIN_STEP'] = '15000'
    os.environ['MAX_STEP'] = '20000'
    
    from action_sync import load_config
    
    try:
        accounts = load_config()
        print(f"✅ 成功加载 {len(accounts)} 个账号")
        for i, account in enumerate(accounts):
            print(f"  账号 {i+1}: {account['mi_user']}")
            print(f"    步数范围: {account['min_step']} - {account['max_step']}")
            print(f"    同步时间: {account['sync_start_hour']}:00 - {account['sync_end_hour']}:00")
        return True
    except Exception as e:
        print(f"❌ 环境变量配置测试失败: {e}")
        return False
    finally:
        # Clean up environment
        for key in ['MI_USER', 'MI_PASSWORD', 'MIN_STEP', 'MAX_STEP']:
            if key in os.environ:
                del os.environ[key]

def test_step_calculation():
    """Test step calculation logic"""
    print("\n=== 步数计算逻辑测试 ===")
    
    from action_sync import get_current_step_range
    
    test_cases = [
        {'hour': 8, 'min_step': 18000, 'max_step': 25000, 'expected_min': 6545, 'expected_max': 9090},
        {'hour': 14, 'min_step': 18000, 'max_step': 25000, 'expected_min': 11454, 'expected_max': 15909},
        {'hour': 22, 'min_step': 18000, 'max_step': 25000, 'expected_min': 18000, 'expected_max': 25000},
    ]
    
    all_passed = True
    for case in test_cases:
        min_step, max_step = get_current_step_range(case['min_step'], case['max_step'], case['hour'])
        
        # Allow some tolerance for rounding
        min_tolerance = abs(min_step - case['expected_min']) <= 100
        max_tolerance = abs(max_step - case['expected_max']) <= 100
        
        if min_tolerance and max_tolerance:
            print(f"✅ {case['hour']}:00 步数计算正确: {min_step} - {max_step}")
        else:
            print(f"❌ {case['hour']}:00 步数计算错误: 期望 {case['expected_min']}-{case['expected_max']}, 实际 {min_step}-{max_step}")
            all_passed = False
    
    return all_passed

def test_mimotion_import():
    """Test MiMotion class import and basic functionality"""
    print("\n=== MiMotion 类导入测试 ===")
    
    try:
        from mimotion_standalone import MiMotion
        
        # Test basic instantiation
        mi = MiMotion("test_user", "test_password")
        print(f"✅ MiMotion 类实例化成功")
        print(f"  用户: {mi.user}")
        print(f"  是否手机号: {mi.is_phone}")
        print(f"  虚拟IP: {mi.fake_ip_addr}")
        
        return True
    except Exception as e:
        print(f"❌ MiMotion 类导入失败: {e}")
        return False

def main():
    """Run all tests"""
    print("MiMotion GitHub Action 功能测试\n")
    
    tests = [
        ("环境变量配置", test_environment_setup),
        ("步数计算逻辑", test_step_calculation),
        ("MiMotion类导入", test_mimotion_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ {test_name}测试出现异常: {e}\n")
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！GitHub Action 实现准备就绪。")
        return 0
    else:
        print("⚠️  有测试失败，请检查实现。")
        return 1

if __name__ == '__main__':
    sys.exit(main())