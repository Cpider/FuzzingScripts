#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fstream>
#include <string>
#include <sstream>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include "llvm/ADT/Statistic.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Support/Debug.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/CallSite.h"
#include "llvm/IR/Instruction.h"
#include "llvm/IR/DebugInfo.h"
#include "llvm/ADT/APInt.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/FileSystem.h"

using namespace llvm;

cl::opt<std::string> OutFile(
    "file",
    cl::desc("Print Function Coverage Name."),
    cl::value_desc("Funciton name output"));

namespace{
    class FunctionCoverage : public ModulePass{

    public :

        static char ID;
        FunctionCoverage() : ModulePass(ID){}
        bool seeded = false;
        bool runOnModule(Module & M) override;
    };


    
}

char FunctionCoverage::ID = 0;

bool FunctionCoverage :: runOnModule(Module &M){

    std::ofstream namefile(OutFile, std::ofstream::out | std::ofstream::app);


    LLVMContext &C = M.getContext();
    IntegerType *Int8Ty = IntegerType::getInt8Ty(C);
    IntegerType *Int32Ty = IntegerType::getInt32Ty(C);
    IntegerType *Int64Ty = IntegerType::getInt64Ty(C);
    // GlobalVariable *output_fd = new GlobalVariable(M, PointerType::get(Int32Ty), false, GlobalValue::ExternalLinkage, 0, "outpu_fd", 
    // 0, GlobalVariable::GeneralDynamicTLSModel, 0, false);
    Function *target_func = M.getFunction("puts");
    if (!target_func)
    {
        SmallVector<Type *, 1> Tys(1, PointerType::get(Int8Ty, 0));
        FunctionType *FT = FunctionType::get(Type::getInt32Ty(C), Tys, /*isVarArg=*/false);
        target_func = Function::Create(FT, Function::ExternalLinkage, "puts", M);
    }

    for(auto &F : M){
        std::string func_print;
        func_print = "Function: " + F.getName().str();
        StringRef Name(func_print);

        // ArrayType *new_type = ArrayType::get(Int8Ty, Name.size());
        Constant *const_string = ConstantDataArray::getString(C, Name);
        GlobalVariable *gvar_array__str = new GlobalVariable(/*Module=*/M,
                                                             /*Type=*/const_string->getType(),
                                                             /*isConstant=*/true,
                                                             /*Linkage=*/GlobalValue::PrivateLinkage,
                                                             /*Initializer=*/0, // has initializer, specified below
                                                             /*Name=*/".str");
        gvar_array__str->setAlignment(1);
        // Constant *const_string = ConstantDataArray::getString(C, Name);

        ConstantInt *const_int = ConstantInt::get(C, APInt(64, StringRef("0"), 10));
        std::vector<Constant *> const_ptr_indices;
        const_ptr_indices.push_back(const_int);
        const_ptr_indices.push_back(const_int);
        // Constant *const_ptr = ConstantExpr::getGetElementPtr(PointerType::get(Int8Ty, 0), gvar_array__str, const_ptr_indices);
        Constant *const_ptr = ConstantExpr::getGetElementPtr(const_string->getType(), gvar_array__str, const_ptr_indices);

        gvar_array__str->setInitializer(const_string);
        BasicBlock *instructed_bb;

        if (F.begin() != F.end()) instructed_bb = (&(*(F.begin())));
        else continue;
        BasicBlock::iterator IP = instructed_bb->getFirstInsertionPt();
        IRBuilder<> IRB(&(*IP));

        std::vector<Value *> args;
        args.push_back(const_ptr);
        IRB.CreateCall(target_func, args);
        errs() << Name << " has instructed sucessed!\n";
        namefile << Name.str() << " has instructed sucessed!\n";


    }
    return true;
}
//clang plugin
// static void registerFunCovPass(const PassManagerBuilder &,
//                             legacy::PassManagerBase &PM)
// {

//     PM.add(new FunctionCoverage());
// }

// static RegisterStandardPasses RegisterFunCovPass(
//     PassManagerBuilder::EP_OptimizerLast, registerFunCovPass);

// static RegisterStandardPasses RegisterFunCovPass0(
//     PassManagerBuilder::EP_EnabledOnOptLevel0, registerFunCovPass);

//opt plugin
static RegisterPass<FunctionCoverage> X("funcov", "hello world pass", false, false);