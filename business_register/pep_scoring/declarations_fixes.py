from typing import List, Callable


class DeclarationsFixSet:
    def get_all_fixes(self) -> List[Callable]:
        fixes = []
        for method_name in dir(self):
            if method_name.startswith('fix_'):
                fixes.append(getattr(self, method_name))
        return fixes

    def run_all_fixes(self):
        for fix_method in self.get_all_fixes():
            fix_method()

    def fix_income_prizes_example_1(self):
        pass

    def fix_income_prizes_example_2(self):
        pass

    def fix_income_prizes_example_3(self):
        pass

    def fix_income_prizes_example_4(self):
        pass
